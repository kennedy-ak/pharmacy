from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('alerts/', views.stock_alerts, name='stock_alerts'),
    path('alerts/<int:pk>/resolve/', views.resolve_alert, name='resolve_alert'),
    path('reports/', views.reports, name='reports'),
]