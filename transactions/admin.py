from django.contrib import admin
from .models import Transaction, TransactionItem, Purchase, Sale


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 1
    fields = ('drug', 'quantity', 'unit_price', 'discount', 'total_price')
    readonly_fields = ('total_price',)


class PurchaseInline(admin.StackedInline):
    model = Purchase
    can_delete = False
    fields = ('supplier', 'invoice_number', 'payment_status', 'payment_due_date')


class SaleInline(admin.StackedInline):
    model = Sale
    can_delete = False
    fields = ('customer_name', 'customer_phone', 'payment_method')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'transaction_type', 'transaction_date', 'total_amount')
    list_filter = ('transaction_type', 'transaction_date')
    search_fields = ('reference_number', 'notes')
    readonly_fields = ('total_amount',)
    date_hierarchy = 'transaction_date'
    inlines = [TransactionItemInline]
    
    def get_inlines(self, request, obj=None):
        inlines = [TransactionItemInline]
        if obj:
            if obj.transaction_type == 'purchase':
                inlines.append(PurchaseInline)
            elif obj.transaction_type == 'sale':
                inlines.append(SaleInline)
        return inlines


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'supplier', 'get_transaction_date', 'payment_status')
    list_filter = ('payment_status', 'supplier')
    search_fields = ('invoice_number', 'transaction__reference_number')
    
    def get_transaction_date(self, obj):
        return obj.transaction.transaction_date
    get_transaction_date.short_description = 'Date'
    get_transaction_date.admin_order_field = 'transaction__transaction_date'


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('get_reference_number', 'customer_name', 'get_transaction_date', 'payment_method')
    list_filter = ('payment_method',)
    search_fields = ('customer_name', 'customer_phone', 'transaction__reference_number')
    
    def get_reference_number(self, obj):
        return obj.transaction.reference_number
    get_reference_number.short_description = 'Reference'
    get_reference_number.admin_order_field = 'transaction__reference_number'
    
    def get_transaction_date(self, obj):
        return obj.transaction.transaction_date
    get_transaction_date.short_description = 'Date'
    get_transaction_date.admin_order_field = 'transaction__transaction_date'