from django.shortcuts import render, get_object_or_404
from .models import DeviceCategory, DeviceDefinition

def device_library_view(request):
    """
    Searchable Device Catalog view.
    """
    category_slug = request.GET.get('category', '').strip()
    search_query = request.GET.get('q', '').strip()

    categories = DeviceCategory.objects.all()
    devices = DeviceDefinition.objects.select_related('category').all()

    if category_slug:
        devices = devices.filter(category__slug=category_slug)
    if search_query:
        devices = devices.filter(name__icontains=search_query) | devices.filter(model_name__icontains=search_query) | devices.filter(description__icontains=search_query)

    context = {
        'categories': categories,
        'devices': devices,
        'selected_category': category_slug,
        'search_query': search_query,
        'page_title': 'Device Library',
    }
    return render(request, 'devices/library.html', context)
