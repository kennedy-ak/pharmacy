from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Drug

@login_required
def drug_api(request, drug_id):
    """
    API to get drug information for AJAX requests
    """
    try:
        drug = Drug.objects.get(pk=drug_id)
        data = {
            'id': drug.id,
            'name': drug.name,
            'unit_price': float(drug.unit_price),
            'selling_price': float(drug.selling_price),
            'quantity_in_stock': drug.quantity_in_stock,
            'is_low_stock': drug.is_low_stock(),
        }
        return JsonResponse(data)
    except Drug.DoesNotExist:
        return JsonResponse({'error': 'Drug not found'}, status=404)