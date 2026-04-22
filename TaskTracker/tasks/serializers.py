from rest_framework import serializers
from django.utils import timezone
from .models import User, Task, Project
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, min_length = 8)
    email = serializers.EmailField(required=True, allow_blank=False)
    username = serializers.CharField(required=True, max_length=128)

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')
        read_only_fields = ('id', 'username', 'email')

class ProjectSerializer(serializers.ModelSerializer):
    # 1. Поле для ЗАПИСИ (принимает список ID пользователей)
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False
    )

    # 2. Поле для ЧТЕНИЯ (возвращает вложенные объекты User)
    participants_info = UserSerializer(
        source='participants', 
        many=True, 
        read_only=True
    )
    
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'creator', 'participants', 'participants_info']
        read_only_fields = ['id', 'creator', 'participants_info']

class TaskSerializer(serializers.ModelSerializer):
    # Поля для ЗАПИСИ (принимают ID)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )

    # Поля для ЧТЕНИЯ (возвращают вложенные объекты)
    project_detail = ProjectSerializer(source='project', read_only=True)
    author_detail = UserSerializer(source='author', read_only=True)
    assignee_detail = UserSerializer(source='assignee', read_only=True)

    # Вычисляемое поле: просрочена ли задача?
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'deadline',
            'project', 'project_detail', 'author', 'author_detail', 
            'assignee', 'assignee_detail', 'is_overdue'
        ]
        read_only_fields = ['id', 'author']  # author подставляется автоматически

    def get_days_until_deadline(self, obj):
        """Возвращает целое число дней до дедлайна. 
        None если дедлайн не указан. 
        Отрицательное число означает, что дедлайн прошёл."""
        if not obj.deadline:
            return None
        
        # ВАЖНО: используем timezone.now(), а не datetime.now()
        # чтобы избежать ошибки сравнения naive и aware объектов при USE_TZ=True
        diff = obj.deadline - timezone.now()

        if diff.days < 0:
            return "Просрочено"

        return diff.days
    
    def validate(self, attrs):
        """Проверка: исполнитель обязан состоять в участниках проекта."""
        assignee = attrs.get('assignee')
        project = attrs.get('project')
        
        if assignee and project:
            # Проверяем, есть ли пользователь в participants проекта
            if not project.participants.filter(id=assignee.id).exists():
                raise serializers.ValidationError({
                    "assignee": "Исполнитель должен быть участником выбранного проекта."
                })
        return attrs
    
    def update(self, instance, validated_data):
        user = self.context['request'].user

        # Исполнитель может менять только статус и приоритет
        if instance.assignee == user and instance.project.creator != user:
            allowed_fields = {'status', 'priority'}
            for field in validated_data:
                if field not in allowed_fields:
                    raise serializers.ValidationError({
                        field: "Исполнитель может изменять только статус и приоритет."
                    })

        # Автор может менять только описание (и удалять, но это отдельный метод destroy)
        if instance.author == user and instance.project.creator != user:
            allowed_fields = {'description'}
            for field in validated_data:
                if field not in allowed_fields:
                    raise serializers.ValidationError({
                        field: "Автор может редактировать только описание задачи."
                    })

        return super().update(instance, validated_data)