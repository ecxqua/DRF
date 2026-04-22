from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Наследование от AbstractUser уже дает: username, password, email, 
    first_name, last_name, is_active, date_joined и хеширование паролей."""
    def __str__(self):
        return self.username


class Project(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    
    # creator: защитный on_delete, чтобы удаление автора не стёрло проект
    creator = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_projects"
    )
    # participants: M2M для требования "Пользователи объединяются в проекты"
    participants = models.ManyToManyField(
        User, related_name="participating_projects", blank=True
    )

    def __str__(self):
        return self.name


class Task(models.Model):
    class Status(models.TextChoices):
        PLANNED = 'PLANNED', 'Запланировано'
        IN_PROGRESS = 'IN_PROGRESS', 'В работе'
        ON_REVIEW = 'ON_REVIEW', 'На проверке'
        DONE = 'DONE', 'Готово'

    class Priority(models.TextChoices):
        HIGH = 'HIGH', 'Высокий'
        MEDIUM = 'MEDIUM', 'Средний'
        LOW = 'LOW', 'Низкий'

    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    
    # Связь с проектом (обратная связь будет доступна через project.tasks)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks"
    )
    # Автор задачи (создатель)
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="authored_tasks"
    )
    # Исполнитель (назначается из участников проекта)
    assignee = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name="assigned_tasks"
    )
    
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PLANNED
    )
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title