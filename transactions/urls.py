from django.urls import path
from . import views

urlpatterns = [
    # Transaction core URLs
    path('', views.transaction_list, name='transaction_list'),
    path('<int:pk>/', views.transaction_detail, name='transaction_detail'),
    path('purchase/create/', views.purchase_create, name='purchase_create'),
    path('sale/create/', views.sale_create, name='sale_create'),
    path('return/create/', views.return_create, name='return_create'),
    path('adjustment/create/', views.adjustment_create, name='adjustment_create'),
    path('<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    
    # API endpoints
    path('api/drug/<int:pk>/', views.drug_api_detail, name='drug_api_detail'),
    path('api/drugs/search/', views.drug_search_api, name='drug_search_api'),
]