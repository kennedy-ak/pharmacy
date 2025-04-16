from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import timedelta
from inventory.models import Drug, Category, Supplier, Batch
from transactions.models import Transaction, TransactionItem
from .models import DailySummary, StockAlert


@login_required
def dashboard_home(request):
    # Get today's date
    today = timezone.now().date()
    
    # Calculate statistics for today
    today_sales = Transaction.objects.filter(
        transaction_type='sale',
        transaction_date__date=today
    ).aggregate(
        total=Sum(
            ExpressionWrapper(
                F('transaction_items__quantity') * F('transaction_items__unit_price'),
                output_field=DecimalField()
            )
        )
    )['total'] or 0
    
    # Get count of transactions today
    sales_count = Transaction.objects.filter(
        transaction_type='sale',
        transaction_date__date=today
    ).count()
    
    # Get count of items sold today
    items_sold = TransactionItem.objects.filter(
        transaction__transaction_type='sale',
        transaction__transaction_date__date=today
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # Low stock alerts
    low_stock_drugs = Drug.objects.filter(quantity_in_stock__lte=F('reorder_level'))
    
    # Expiring drugs (expiring in the next 30 days)
    thirty_days_later = today + timedelta(days=30)
    expiring_drugs = Drug.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=thirty_days_later
    )
    
    # Recently added drugs
    recent_drugs = Drug.objects.all().order_by('-created_at')[:5]
    
    # Recent transactions
    recent_transactions = Transaction.objects.all().order_by('-transaction_date')[:5]
    
    # Get top selling drugs
    last_30_days = today - timedelta(days=30)
    top_selling_drugs = TransactionItem.objects.filter(
        transaction__transaction_type='sale',
        transaction__transaction_date__date__gte=last_30_days
    ).values('drug__name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]
    
    context = {
        'today_sales': today_sales,
        'sales_count': sales_count,
        'items_sold': items_sold,
        'low_stock_count': low_stock_drugs.count(),
        'expiring_count': expiring_drugs.count(),
        'low_stock_drugs': low_stock_drugs,
        'expiring_drugs': expiring_drugs,
        'recent_drugs': recent_drugs,
        'recent_transactions': recent_transactions,
        'top_selling_drugs': top_selling_drugs,
        'total_drugs': Drug.objects.count(),
        'total_categories': Category.objects.count(),
        'total_suppliers': Supplier.objects.count(),
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def stock_alerts(request):
    # Get all active alerts
    alerts = StockAlert.objects.filter(is_resolved=False).order_by('-created_at')
    
    # Check for new low stock drugs
    low_stock_drugs = Drug.objects.filter(quantity_in_stock__lte=F('reorder_level'))
    
    # Create alerts for drugs that don't already have an active alert
    for drug in low_stock_drugs:
        existing_alert = StockAlert.objects.filter(
            drug_name=drug.name,
            alert_type='low_stock',
            is_resolved=False
        ).exists()
        
        if not existing_alert:
            StockAlert.objects.create(
                drug_name=drug.name,
                alert_type='low_stock',
                message=f"Low stock alert: {drug.name} has only {drug.quantity_in_stock} units left."
            )
    
    # Check for expiring drugs (expiring in the next 30 days)
    today = timezone.now().date()
    thirty_days_later = today + timedelta(days=30)
    
    expiring_drugs = Drug.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=thirty_days_later
    )
    
    # Create alerts for drugs that don't already have an active alert
    for drug in expiring_drugs:
        existing_alert = StockAlert.objects.filter(
            drug_name=drug.name,
            alert_type='expiry',
            is_resolved=False
        ).exists()
        
        if not existing_alert:
            days_remaining = (drug.expiry_date - today).days
            StockAlert.objects.create(
                drug_name=drug.name,
                alert_type='expiry',
                message=f"Expiry alert: {drug.name} will expire in {days_remaining} days."
            )
    
    # Refresh the alerts query to include newly created alerts
    alerts = StockAlert.objects.filter(is_resolved=False).order_by('-created_at')
    
    context = {
        'alerts': alerts,
        'low_stock_count': low_stock_drugs.count(),
        'expiring_count': expiring_drugs.count(),
    }
    
    return render(request, 'dashboard/stock_alerts.html', context)


@login_required
def resolve_alert(request, pk):
    alert = StockAlert.objects.get(pk=pk)
    alert.resolve()
    return redirect('stock_alerts')


@login_required
def reports(request):
    # Get date range from request or default to last 30 days
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    today = timezone.now().date()
    
    if not start_date:
        start_date = today - timedelta(days=30)
    else:
        # Parse the date from the request
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = today
    else:
        # Parse the date from the request
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get sales data for the date range
    sales_data = Transaction.objects.filter(
        transaction_type='sale',
        transaction_date__date__gte=start_date,
        transaction_date__date__lte=end_date
    )
    
    # Calculate total sales
    total_sales = sales_data.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('transaction_items__quantity') * F('transaction_items__unit_price'),
                output_field=DecimalField()
            )
        )
    )['total'] or 0
    
    # Get purchases data for the date range
    purchases_data = Transaction.objects.filter(
        transaction_type='purchase',
        transaction_date__date__gte=start_date,
        transaction_date__date__lte=end_date
    )
    
    # Calculate total purchases
    total_purchases = purchases_data.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('transaction_items__quantity') * F('transaction_items__unit_price'),
                output_field=DecimalField()
            )
        )
    )['total'] or 0
    
    # Get top selling drugs for the period
    top_selling_drugs = TransactionItem.objects.filter(
        transaction__transaction_type='sale',
        transaction__transaction_date__date__gte=start_date,
        transaction__transaction_date__date__lte=end_date
    ).values('drug__name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(
            ExpressionWrapper(
                F('quantity') * F('unit_price'),
                output_field=DecimalField()
            )
        )
    ).order_by('-total_sold')[:10]
    
    # Get sales by category
    sales_by_category = TransactionItem.objects.filter(
        transaction__transaction_type='sale',
        transaction__transaction_date__date__gte=start_date,
        transaction__transaction_date__date__lte=end_date
    ).values('drug__category__name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(
            ExpressionWrapper(
                F('quantity') * F('unit_price'),
                output_field=DecimalField()
            )
        )
    ).order_by('-total_revenue')
    days_in_range = (end_date - start_date).days + 1 
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'profit': total_sales - total_purchases,
        'sales_count': sales_data.count(),
        'purchases_count': purchases_data.count(),
        'top_selling_drugs': top_selling_drugs,
        'sales_by_category': sales_by_category,
        'days_in_range': days_in_range, 
    }
    
    return render(request, 'dashboard/reports.html', context)