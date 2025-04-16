from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Drug(models.Model):
    name = models.CharField(max_length=100)
    generic_name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='drugs')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='drugs')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], editable=False)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    expiry_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Calculate selling price as unit price + 30%
        self.selling_price =self.unit_price * Decimal('1.3')
        super().save(*args, **kwargs)
    
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level
    
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date <= timezone.now().date()
        return False
    
    def __str__(self):
        return self.name


class Batch(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()
    date_received = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return self.expiry_date <= timezone.now().date()
    
    def __str__(self):
        return f"{self.drug.name} - {self.batch_number}"
    
    class Meta:
        verbose_name_plural = "Batches"