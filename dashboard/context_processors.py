from .models import StockAlert

def alert_count(request):
    """
    Context processor to provide alert count to all templates
    """
    count = 0
    if request.user.is_authenticated:
        count = StockAlert.objects.filter(is_resolved=False).count()
    
    return {'alert_count': count}