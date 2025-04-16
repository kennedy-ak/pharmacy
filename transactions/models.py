from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from inventory.models import Drug, Supplier


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
    
     
    )
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference_number = models.CharField(max_length=50, unique=True)
    transaction_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.reference_number}"
    
    @property
    def total_amount(self):
        return sum(item.total_price for item in self.transaction_items.all())


class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, related_name='transaction_items', on_delete=models.CASCADE)
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    def __str__(self):
        return f"{self.drug.name} - {self.quantity}"
    
    @property
    def total_price(self):
        return (self.unit_price * self.quantity) - self.discount
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Update inventory only if the item is being saved for the first time
        if is_new:
            drug = self.drug
            
            if self.transaction.transaction_type == 'purchase':
                drug.quantity_in_stock += self.quantity
            elif self.transaction.transaction_type == 'sale':
                if drug.quantity_in_stock >= self.quantity:
                    drug.quantity_in_stock -= self.quantity
            elif self.transaction.transaction_type == 'return':
                drug.quantity_in_stock += self.quantity
            elif self.transaction.transaction_type == 'adjustment':
                # For adjustment, the quantity represents the new total, not the difference
                difference = self.quantity - drug.quantity_in_stock
                drug.quantity_in_stock = self.quantity
            
            drug.save()


class Purchase(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='purchase')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=20, choices=(
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('unpaid', 'Unpaid'),
    ), default='unpaid')
    payment_due_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"Purchase - {self.invoice_number}"


class Sale(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='sale')
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=(
        ('cash', 'Cash'),
    
        ('mobile', 'Mobile Payment'),
       
    ), default='cash')
    
    def __str__(self):
        return f"Sale - {self.transaction.reference_number}"