from django.contrib import admin
from .models import DailySummary, StockAlert


@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'total_purchases', 'profit', 'items_sold')
    list_filter = ('date',)
    date_hierarchy = 'date'
    readonly_fields = ('date', 'total_sales', 'total_purchases', 'profit', 'items_sold')


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ('drug_name', 'alert_type', 'is_resolved', 'created_at', 'resolved_at')
    list_filter = ('alert_type', 'is_resolved', 'created_at')
    search_fields = ('drug_name', 'message')
    readonly_fields = ('drug_name', 'alert_type', 'message', 'created_at')
    actions = ['mark_as_resolved']
    
    def mark_as_resolved(self, request, queryset):
        for alert in queryset:
            alert.resolve()
        self.message_user(request, f"{queryset.count()} alerts marked as resolved.")
    mark_as_resolved.short_description = "Mark selected alerts as resolved"