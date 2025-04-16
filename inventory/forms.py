from django import forms
from .models import Drug, Category, Supplier, Batch


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class DrugForm(forms.ModelForm):
    class Meta:
        model = Drug
        fields = [
            'name', 'generic_name', 'description', 'category', 
            'supplier', 'unit_price', 'quantity_in_stock', 
            'reorder_level', 'expiry_date'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price <= 0:
            raise forms.ValidationError("Unit price must be greater than zero.")
        return unit_price


class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['batch_number', 'quantity', 'expiry_date', 'date_received']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'date_received': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity
    
    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date')
        date_received = self.cleaned_data.get('date_received')
        
        if expiry_date and date_received and expiry_date <= date_received:
            raise forms.ValidationError("Expiry date must be later than date received.")
        
        return expiry_date