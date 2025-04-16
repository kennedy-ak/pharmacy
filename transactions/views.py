from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q

from .models import Transaction, TransactionItem, Purchase, Sale
from inventory.models import Drug, Supplier
from .forms import TransactionForm, TransactionItemForm, PurchaseForm, SaleForm
import uuid


@login_required
def transaction_list(request):
    transaction_type = request.GET.get('type', '')
    
    transactions = Transaction.objects.all().order_by('-transaction_date')
    
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    context = {
        'transactions': transactions,
        'selected_type': transaction_type,
    }
    
    return render(request, 'transactions/transaction_list.html', context)


@login_required
def transaction_detail(request, pk):
    transaction_obj = get_object_or_404(Transaction, pk=pk)
    items = transaction_obj.transaction_items.all()
    
    # Get related purchase or sale if exists
    related_obj = None
    if transaction_obj.transaction_type == 'purchase':
        try:
            related_obj = transaction_obj.purchase
        except Purchase.DoesNotExist:
            pass
    elif transaction_obj.transaction_type == 'sale':
        try:
            related_obj = transaction_obj.sale
        except Sale.DoesNotExist:
            pass
    
    context = {
        'transaction': transaction_obj,
        'items': items,
        'related_obj': related_obj,
        'now': timezone.now(),
    }
    
    return render(request, 'transactions/transaction_detail.html', context)


@login_required
@transaction.atomic
def purchase_create(request):
    TransactionItemFormSet = inlineformset_factory(
        Transaction, 
        TransactionItem, 
        form=TransactionItemForm,
        extra=1,
        can_delete=False
    )
    
    if request.method == 'POST':
        transaction_form = TransactionForm(
            request.POST, 
            initial={'transaction_type': 'purchase'}
        )
        transaction_form.fields['transaction_type'].widget.attrs['readonly'] = True
        
        purchase_form = PurchaseForm(request.POST)
        
        if transaction_form.is_valid():
            transaction_obj = transaction_form.save(commit=False)
            transaction_obj.transaction_type = 'purchase'
            transaction_obj.reference_number = f"PUR-{uuid.uuid4().hex[:8].upper()}"
            transaction_obj.save()
            
            formset = TransactionItemFormSet(request.POST, instance=transaction_obj)
            
            if formset.is_valid() and purchase_form.is_valid():
                formset.save()
                
                purchase = purchase_form.save(commit=False)
                purchase.transaction = transaction_obj
                purchase.save()
                
                messages.success(request, 'Purchase has been created successfully!')
                return redirect('transaction_detail', pk=transaction_obj.pk)
            else:
                # If we get here with validation errors but the transaction was created, delete it
                transaction_obj.delete()
        
        # If we get here, there's a form error
        formset = TransactionItemFormSet(request.POST)
    else:
        transaction_form = TransactionForm(
            initial={'transaction_type': 'purchase'}
        )
        transaction_form.fields['transaction_type'].widget.attrs['readonly'] = True
        
        purchase_form = PurchaseForm()
        formset = TransactionItemFormSet()
    
    context = {
        'transaction_form': transaction_form,
        'purchase_form': purchase_form,
        'formset': formset,
        'title': 'Create Purchase',
    }
    
    return render(request, 'transactions/purchase_form.html', context)


@login_required
@transaction.atomic
def sale_create(request):
    TransactionItemFormSet = inlineformset_factory(
        Transaction, 
        TransactionItem, 
        form=TransactionItemForm,
        extra=1,
        can_delete=False
    )
    
    if request.method == 'POST':
        transaction_form = TransactionForm(
            request.POST, 
            initial={'transaction_type': 'sale'}
        )
        transaction_form.fields['transaction_type'].widget.attrs['readonly'] = True
        
        sale_form = SaleForm(request.POST)
        
        if transaction_form.is_valid():
            transaction_obj = transaction_form.save(commit=False)
            transaction_obj.transaction_type = 'sale'
            transaction_obj.reference_number = f"SAL-{uuid.uuid4().hex[:8].upper()}"
            transaction_obj.save()
            
            formset = TransactionItemFormSet(request.POST, instance=transaction_obj)
            
            if formset.is_valid() and sale_form.is_valid():
                # Check if we have enough stock for all items
                can_process = True
                for form in formset:
                    if form.is_valid() and form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        drug = form.cleaned_data.get('drug')
                        quantity = form.cleaned_data.get('quantity', 0)
                        
                        if drug and drug.quantity_in_stock < quantity:
                            form.add_error('quantity', f'Not enough stock. Only {drug.quantity_in_stock} available.')
                            can_process = False
                
                if can_process:
                    formset.save()
                    
                    sale = sale_form.save(commit=False)
                    sale.transaction = transaction_obj
                    sale.save()
                    
                    messages.success(request, 'Sale has been created successfully!')
                    return redirect('transaction_detail', pk=transaction_obj.pk)
                else:
                    # Keep the transaction but don't process it yet
                    pass
            else:
                # If we get here with validation errors but the transaction was created, delete it
                transaction_obj.delete()
        
        # If we get here, there's a form error
        formset = TransactionItemFormSet(request.POST)
    else:
        transaction_form = TransactionForm(
            initial={'transaction_type': 'sale'}
        )
        transaction_form.fields['transaction_type'].widget.attrs['readonly'] = True
        
        sale_form = SaleForm()
        formset = TransactionItemFormSet()
    
    context = {
        'transaction_form': transaction_form,
        'sale_form': sale_form,
        'formset': formset,
        'title': 'Create Sale',
    }
    
    return render(request, 'transactions/sale_form.html', context)


@login_required
def transaction_delete(request, pk):
    transaction_obj = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        # Handle inventory updates before deletion
        if transaction_obj.transaction_type == 'purchase':
            # Reverse the purchase by reducing inventory
            for item in transaction_obj.transaction_items.all():
                drug = item.drug
                drug.quantity_in_stock -= item.quantity
                drug.save()
        elif transaction_obj.transaction_type == 'sale':
            # Reverse the sale by increasing inventory
            for item in transaction_obj.transaction_items.all():
                drug = item.drug
                drug.quantity_in_stock += item.quantity
                drug.save()
        
        transaction_obj.delete()
        messages.success(request, 'Transaction has been deleted successfully!')
        return redirect('transaction_list')
    
    context = {
        'transaction': transaction_obj,
    }
    
    return render(request, 'transactions/transaction_confirm_delete.html', context)


@login_required
@transaction.atomic
def return_create(request):
    TransactionItemFormSet = inlineformset_factory(
        Transaction, 
        TransactionItem, 
        form=TransactionItemForm,
        extra=1,
        can_delete=False
    )
    
    if request.method == 'POST':
        transaction_form = TransactionForm(
            request.POST, 
            initial={'transaction_type': 'return'}
        )
        transaction_form.fields['transaction_type'].widget.attrs['readonly'] = True
        
        if transaction_form.is_valid():
            transaction_obj = transaction_form.save(commit=False)
            transaction_obj.transaction_type = 'return'
            transaction_obj.reference_number = f"RET-{uuid.uuid4().hex[:8].upper()}"
            transaction_obj.save()
            
            formset = TransactionItemFormSet(request.POST, instance=transaction_obj)
            
            if formset.is_valid():
                formset.save()
                
                messages.success(request, 'Return has been processed successfully!')
                return redirect('transaction_detail', pk=transaction_obj.pk)
            else:
                # If we get here with validation errors but the transaction was created, delete it
                transaction_obj.delete()
        
        # If we get here, there's a form error
        formset = TransactionItemFormSet(request.POST)
    else:
        transaction_form = TransactionForm(
            initial={'transaction_type': 'return'}
        )
        transaction_form.fields['transaction_type'].widget.attrs['readonly'] = True
        
        formset = TransactionItemFormSet()
    
    context = {
        'transaction_form': transaction_form,
        'formset': formset,
        'title': 'Process Return',
    }
    
    return render(request, 'transactions/return_form.html', context)


@login_required
@transaction.atomic
def adjustment_create(request):
    TransactionItemFormSet = inlineformset_factory(
        Transaction, 
        TransactionItem, 
        form=TransactionItemForm,
        extra=1,
        can_delete=False
    )
    
    if request.method == 'POST':
        transaction_form = TransactionForm(
            request.POST, 
            initial={'transaction_type': 'adjustment'}
        )
        transaction_form.fields['transaction_type'].widget.attrs['readonly'] = True
        
        if transaction_form.is_valid():
            transaction_obj = transaction_form.save(commit=False)
            transaction_obj.transaction_type = 'adjustment'
            transaction_obj.reference_number = f"ADJ-{uuid.uuid4().hex[:8].upper()}"
            transaction_obj.save()
            
            formset = TransactionItemFormSet(request.POST, instance=transaction_obj)
            
            if formset.is_valid():
                formset.save()
                
                messages.success(request, 'Inventory adjustment has been processed successfully!')
                return redirect('transaction_detail', pk=transaction_obj.pk)
            else:
                # If we get here with validation errors but the transaction was created, delete it
                transaction_obj.delete()
        
        # If we get here, there's a form error
        formset = TransactionItemFormSet(request.POST)
    else:
        transaction_form = TransactionForm(
            initial={'transaction_type': 'adjustment'}
        )
        transaction_form.fields['transaction_type'].widget.attrs['readonly'] = True
        
        formset = TransactionItemFormSet()
    
    context = {
        'transaction_form': transaction_form,
        'formset': formset,
        'title': 'Inventory Adjustment',
    }
    
    return render(request, 'transactions/adjustment_form.html', context)


# API endpoints
def drug_api_detail(request, pk):
    """API endpoint to get drug information including selling price."""
    drug = get_object_or_404(Drug, pk=pk)
    data = {
        'id': drug.id,
        'name': drug.name,
        'selling_price': float(drug.selling_price),
        'quantity_in_stock': drug.quantity_in_stock
    }
    return JsonResponse(data)


def drug_search_api(request):
    """API endpoint to search drugs by name or generic name."""
    query = request.GET.get('term', '')
    
    if query:
        drugs = Drug.objects.filter(
            Q(name__icontains=query) | 
            Q(generic_name__icontains=query)
        ).filter(quantity_in_stock__gt=0)[:10]  # Limit to 10 results with stock available
        
        results = [{
            'id': drug.id,
            'text': f"{drug.name} ({drug.generic_name})" if drug.generic_name and drug.generic_name.strip() else drug.name,
            'selling_price': float(drug.selling_price),
            'stock': drug.quantity_in_stock
        } for drug in drugs]
        
        return JsonResponse({'results': results})
    
    return JsonResponse({'results': []})