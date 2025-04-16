from django.db import models
from django.utils import timezone


class DailySummary(models.Model):
    date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_purchases = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    items_sold = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Summary for {self.date}"
    
    class Meta:
        verbose_name_plural = "Daily Summaries"


class StockAlert(models.Model):
    ALERT_TYPES = (
        ('low_stock', 'Low Stock'),
        ('expiry', 'Expiry Alert'),
    )
    
    drug_name = models.CharField(max_length=100)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.drug_name}"
    
    def resolve(self):
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.save()