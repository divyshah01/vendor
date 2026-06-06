# core/vendor_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Vendor, User

@login_required
def vendor_list_view(request):
    # Restrict viewing authorization to Admins, Managers, and Procurement Officers
    if request.user.role not in ['ADMIN', 'PROCUREMENT_OFFICER', 'MANAGER']:
        messages.error(request, "Unauthorized access to the corporate Vendor Directory.")
        return redirect('dashboard')

    query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')

    vendors = Vendor.objects.all()

    # Apply search filter matching name, category, or GST values
    if query:
        vendors = vendors.filter(
            Q(company_name__icontains=query) | 
            Q(gst_number__icontains=query) |
            Q(category__icontains=query)
        )
    
    if category_filter:
        vendors = vendors.filter(category=category_filter)
        
    if status_filter:
        vendors = vendors.filter(status=status_filter)

    # Fetch unique categories for the filter dropdown matrix
    categories = Vendor.objects.values_list('category', flat=True).distinct()

    context = {
        'vendors': vendors,
        'categories': categories,
        'search_query': query,
        'selected_category': category_filter,
        'selected_status': status_filter,
    }
    return render(request, 'vendors/vendor_list.html', context)


@login_required
def register_vendor_view(request):
    if request.user.role not in ['ADMIN', 'PROCUREMENT_OFFICER']:
        messages.error(request, "Unauthorized to register new vendor accounts.")
        return redirect('vendor_list')

    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        category = request.POST.get('category')
        gst_number = request.POST.get('gst_number')
        contact_email = request.POST.get('contact_email')
        contact_phone = request.POST.get('contact_phone')
        address = request.POST.get('address')

        # Simple verification checks
        if Vendor.objects.filter(gst_number=gst_number).exists():
            messages.error(request, "A vendor matching this GST details registry code already exists.")
        else:
            Vendor.objects.create(
                company_name=company_name,
                category=category,
                gst_number=gst_number,
                contact_email=contact_email,
                contact_phone=contact_phone,
                address=address,
                status='PENDING'
            )
            messages.success(request, f"Vendor account '{company_name}' registered successfully.")
            return redirect('vendor_list')

    return render(request, 'vendors/register_vendor.html')


@login_required
def update_vendor_status_view(request, vendor_id):
    if request.user.role not in ['ADMIN', 'MANAGER']:
        messages.error(request, "Unauthorized to alter vendor statuses.")
        return redirect('vendor_list')

    vendor = get_object_or_404(Vendor, id=vendor_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['ACTIVE', 'PENDING', 'INACTIVE']:
            vendor.status = new_status
            vendor.save()
            messages.success(request, f"Status updated for {vendor.company_name} to {vendor.get_status_display()}.")
    
    return redirect('vendor_list')