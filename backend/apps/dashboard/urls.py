from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('ranking/', views.RankingView.as_view(), name='employee-ranking'),
]