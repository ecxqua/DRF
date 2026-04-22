from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# Импортируем только ViewSet для API
from tasks.views import ProjectViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project-api')
router.register(r'tasks', TaskViewSet, basename='task-api')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 🔹 API маршруты
    path('api/', include(router.urls)),
    
    # 🔹 JWT аутентификация
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 🔹 Документация (Swagger/ReDoc)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]