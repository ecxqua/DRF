
from .models import Task, Project, User
from .serializers import TaskSerializer, ProjectSerializer
from .permissions import TaskPermission
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.utils import timezone


# ========== API VIEWSETS ==========

class StandardPagination(PageNumberPagination):
    """Кастомная пагинация с возможностью изменения размера страницы."""
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 5


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        """Пользователь видит только проекты, где он: создатель или участник."""
        return Project.objects.filter(
            Q(creator=self.request.user) | Q(participants=self.request.user)
        ).distinct().prefetch_related('participants')

    def perform_create(self, serializer):
        """Создатель проекта фиксируется автоматически из сессии."""
        serializer.save(creator=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [TaskPermission]
    pagination_class = StandardPagination

    # Бэкенды для фильтрации, сортировки и поиска
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'priority', 'assignee', 'deadline']
    ordering_fields = ['deadline', 'priority', 'created_at']
    search_fields = ['title', 'description']

    def get_queryset(self):
        """
        Изоляция данных: пользователь видит только задачи проектов, 
        в которых он является участником или создателем.
        """
        return Task.objects.filter(
            project__participants=self.request.user
        ).select_related('project', 'author', 'assignee').prefetch_related('project__participants')

    def perform_create(self, serializer):
        """
        Автор задачи фиксируется автоматически из сессии.
        Проект уже передан клиентом и прошёл валидацию.
        """
        serializer.save(author=self.request.user)

