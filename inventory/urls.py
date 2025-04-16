from django.urls import path
from . import views


urlpatterns = [
    path('', views.inventory_home, name='inventory_home'),
    path('drugs/', views.drug_list, name='drug_list'),
    path('drugs/<int:pk>/', views.drug_detail, name='drug_detail'),
    path('drugs/create/', views.drug_create, name='drug_create'),
    path('drugs/<int:pk>/update/', views.drug_update, name='drug_update'),
    path('drugs/<int:drug_id>/add-batch/', views.batch_create, name='batch_create'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    
    # API endpoint

]