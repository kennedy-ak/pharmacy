from django.contrib import admin
from .models import Category, Supplier, Drug, Batch


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email')
    search_fields = ('name', 'contact_person', 'email')
    list_filter = ('created_at',)


class BatchInline(admin.TabularInline):
    model = Batch
    extra = 1
    fields = ('batch_number', 'quantity', 'expiry_date', 'date_received')


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ('name', 'generic_name', 'category', 'supplier', 'unit_price', 
                    'selling_price', 'quantity_in_stock', 'is_low_stock', 'expiry_date')
    list_filter = ('category', 'supplier', 'created_at')
    search_fields = ('name', 'generic_name')
    readonly_fields = ('selling_price',)
    inlines = [BatchInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'generic_name', 'description', 'category', 'supplier')
        }),
        ('Pricing', {
            'fields': ('unit_price', 'selling_price')
        }),
        ('Inventory', {
            'fields': ('quantity_in_stock', 'reorder_level', 'expiry_date')
        }),
    )


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('drug', 'batch_number', 'quantity', 'expiry_date', 'date_received', 'is_expired')
    list_filter = ('date_received', 'expiry_date')
    search_fields = ('batch_number', 'drug__name')
    date_hierarchy = 'date_received'