# procurement/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import RFQ
from core.models import Vendor

@login_required
def rfq_list_view(request):
    user = request.user
    # View logic splits based on active operational role
    if user.role in ['ADMIN', 'PROCUREMENT_OFFICER', 'MANAGER']:
        rfqs = RFQ.objects.all().order_by('-created_at')
    elif user.role == 'VENDOR' and hasattr(user, 'vendor_profile'):
        rfqs = RFQ.objects.filter(assigned_vendors=user.vendor_profile, status='OPEN').order_by('-created_at')
    else:
        rfqs = []
        
    return render(request, 'procurement/rfq_list.html', {'rfqs': rfqs})


@login_required
def create_rfq_view(request):
    if request.user.role not in ['ADMIN', 'PROCUREMENT_OFFICER']:
        messages.error(request, "Access restricted. Only Procurement Officers can build RFQ structures.")
        return redirect('rfq_list')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        product_details = request.POST.get('product_details')
        quantity = request.POST.get('quantity')
        deadline = request.POST.get('deadline')
        vendor_ids = request.POST.getlist('vendors')
        attachments = request.FILES.get('attachments')

        try:
            # Construct base entity framework log object
            rfq = RFQ.objects.create(
                title=title,
                description=description,
                product_details=product_details,
                quantity=quantity,
                deadline=deadline,
                status='OPEN',  # Automatically push live to vendors upon save
                created_by=request.user,
                attachments=attachments
            )
            
            # Form relationship joins with assigned vendors
            if vendor_ids:
                vendors = Vendor.objects.filter(id__in=vendor_ids, status='ACTIVE')
                rfq.assigned_vendors.set(vendors)
            
            rfq.save()
            messages.success(request, f"RFQ '{title}' successfully initialized and dispatched to vendors.")
            return redirect('rfq_list')
            
        except Exception as e:
            messages.error(request, f"Error compiling database entries: {str(e)}")

    # Fetch active verified vendor directory profiles to populate multi-select field options
    active_vendors = Vendor.objects.filter(status='ACTIVE')
    return render(request, 'procurement/create_rfq.html', {'vendors': active_vendors})