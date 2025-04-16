from django import forms
from .models import Transaction, TransactionItem, Purchase, Sale
from inventory.models import Drug


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'transaction_date', 'notes']
        widgets = {
            'transaction_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class TransactionItemForm(forms.ModelForm):
    class Meta:
        model = TransactionItem
        fields = ['drug', 'quantity', 'unit_price']
        widgets = {
            'drug': forms.Select(attrs={'class': 'form-control select-drug'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '1'}),
            'unit_price': forms.HiddenInput(),  # Hidden as we'll use selling_price
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make the drug field searchable
        self.fields['drug'].widget.attrs.update({'class': 'form-control select-drug'})
        
        # Set the initial unit price based on the selected drug's selling price
        if self.instance and self.instance.pk and self.instance.drug:
            self.fields['unit_price'].initial = self.instance.drug.selling_price
    
    def clean(self):
        cleaned_data = super().clean()
        drug = cleaned_data.get('drug')
        quantity = cleaned_data.get('quantity')
        transaction = self.instance.transaction if self.instance and hasattr(self.instance, 'transaction') else None
        
        if drug and quantity and transaction and transaction.transaction_type == 'sale':
            if quantity > drug.quantity_in_stock:
                self.add_error('quantity', f'Not enough stock. Only {drug.quantity_in_stock} available.')
        
        return cleaned_data


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['supplier', 'invoice_number', 'payment_status', 'payment_due_date']
        widgets = {
            'payment_due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer_name', 'customer_phone', 'payment_method']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }