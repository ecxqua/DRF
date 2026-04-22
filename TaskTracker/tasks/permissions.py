from rest_framework.permissions import BasePermission, SAFE_METHODS

class TaskPermission(BasePermission):
    """
    Кастомные права доступа к задачам:
    - Владелец проекта: полный доступ (CRUD)
    - Автор задачи: удаление + редактирование описания
    - Исполнитель: изменение статуса и приоритета
    - Остальные участники: только чтение
    """
    def has_object_permission(self, request, view, obj):
        # Чтение (GET, HEAD, OPTIONS) — разрешено всем участникам проекта
        if request.method in SAFE_METHODS:
            return True

        # Создатель проекта — полный доступ к любым задачам проекта
        if obj.project.creator == request.user:
            return True

        # Автор задачи — удаление и обновление
        if obj.author == request.user:
            if view.action == 'destroy':
                return True
            if view.action in ('update', 'partial_update'):
                # Разрешаем запрос, но ограничиваем поля в сериализаторе
                return True

        # Исполнитель — только обновление (статус/приоритет)
        if obj.assignee == request.user and view.action in ('update', 'partial_update'):
            return True

        # Все остальные действия запрещены
        return False