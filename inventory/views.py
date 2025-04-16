from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q, Sum, ExpressionWrapper, DecimalField
from .models import Category, Supplier, Drug, Batch
from .forms import DrugForm, BatchForm, CategoryForm, SupplierForm

from django.utils import timezone
@login_required
def inventory_home(request):
    low_stock_drugs = Drug.objects.filter(quantity_in_stock__lte=models.F('reorder_level'))
    expired_drugs = Drug.objects.filter(expiry_date__lte=timezone.now().date())
    
    context = {
        'total_drugs': Drug.objects.count(),
        'total_categories': Category.objects.count(),
        'total_suppliers': Supplier.objects.count(),
        'low_stock_count': low_stock_drugs.count(),
        'expired_count': expired_drugs.count(),
    }
    
    return render(request, 'inventory/dashboard.html', context)



@login_required
def inventory_home(request):
    low_stock_drugs = Drug.objects.filter(quantity_in_stock__lte=F('reorder_level'))
    expired_drugs = Drug.objects.filter(expiry_date__lte=timezone.now().date())
    
    context = {
        'total_drugs': Drug.objects.count(),
        'total_categories': Category.objects.count(),
        'total_suppliers': Supplier.objects.count(),
        'low_stock_count': low_stock_drugs.count(),
        'expired_count': expired_drugs.count(),
        'low_stock_drugs': low_stock_drugs[:5],
        'expired_drugs': expired_drugs[:5],
    }
    
    return render(request, 'inventory/dashboard.html', context)

@login_required
def drug_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    supplier_id = request.GET.get('supplier', '')
    
    drugs = Drug.objects.all()
    
    if query:
        drugs = drugs.filter(
            Q(name__icontains=query) | 
            Q(generic_name__icontains=query) |
            Q(description__icontains=query)
        )
    
    if category_id:
        drugs = drugs.filter(category_id=category_id)
    
    if supplier_id:
        drugs = drugs.filter(supplier_id=supplier_id)
    
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()
    
    context = {
        'drugs': drugs,
        'categories': categories,
        'suppliers': suppliers,
        'query': query,
        'selected_category': int(category_id) if category_id else None,
        'selected_supplier': int(supplier_id) if supplier_id else None,
    }
    
    return render(request, 'inventory/drug_list.html', context)


@login_required
def drug_detail(request, pk):
    drug = get_object_or_404(Drug, pk=pk)
    batches = drug.batches.all().order_by('-date_received')
    
    context = {
        'drug': drug,
        'batches': batches,
    }
    
    return render(request, 'inventory/drug_detail.html', context)


@login_required
def drug_create(request):
    if request.method == 'POST':
        form = DrugForm(request.POST)
        if form.is_valid():
            drug = form.save()
            messages.success(request, f'Drug "{drug.name}" has been created successfully!')
            return redirect('drug_detail', pk=drug.pk)
    else:
        form = DrugForm()
    
    context = {
        'form': form,
        'title': 'Add New Drug',
    }
    
    return render(request, 'inventory/drug_form.html', context)


@login_required
def drug_update(request, pk):
    drug = get_object_or_404(Drug, pk=pk)
    
    if request.method == 'POST':
        form = DrugForm(request.POST, instance=drug)
        if form.is_valid():
            drug = form.save()
            messages.success(request, f'Drug "{drug.name}" has been updated successfully!')
            return redirect('drug_detail', pk=drug.pk)
    else:
        form = DrugForm(instance=drug)
    
    context = {
        'form': form,
        'drug': drug,
        'title': 'Update Drug',
    }
    
    return render(request, 'inventory/drug_form.html', context)


@login_required
def batch_create(request, drug_id):
    drug = get_object_or_404(Drug, pk=drug_id)
    
    if request.method == 'POST':
        form = BatchForm(request.POST)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.drug = drug
            batch.save()
            
            # Update drug quantity
            drug.quantity_in_stock += batch.quantity
            drug.save()
            
            messages.success(request, f'New batch for "{drug.name}" has been added successfully!')
            return redirect('drug_detail', pk=drug.pk)
    else:
        form = BatchForm()
    
    context = {
        'form': form,
        'drug': drug,
        'title': f'Add New Batch for {drug.name}',
    }
    
    return render(request, 'inventory/batch_form.html', context)


@login_required
def category_list(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'inventory/category_list.html', context)


@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" has been created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Add New Category',
    }
    
    return render(request, 'inventory/category_form.html', context)


@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    context = {'suppliers': suppliers}
    return render(request, 'inventory/supplier_list.html', context)


@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier "{supplier.name}" has been created successfully!')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    
    context = {
        'form': form,
        'title': 'Add New Supplier',
    }
    
    return render(request, 'inventory/supplier_form.html', context)