from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'config', views.ConnectorConfigViewSet, basename='connector-config')
router.register(r'sync-logs', views.SyncLogViewSet, basename='sync-log')
router.register(r'sync', views.SyncTriggerView, basename='sync-trigger')

urlpatterns = [
    path('', include(router.urls)),
]