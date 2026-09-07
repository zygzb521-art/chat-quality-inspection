from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/conversations/', include('apps.conversations.urls')),
    path('api/violations/', include('apps.reviews.urls')),
    path('api/rules/', include('apps.rules.urls')),
    path('api/platforms/', include('apps.connectors.urls')),
    path('api/ai/', include('apps.ai_analysis.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/training/', include('apps.training.urls')),
]