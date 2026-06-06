# procurement/quotation_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import RFQ, Quotation

@login_required
def submit_quotation_view(request, rfq_id):
    # Verify that the active session user is mapped to an active Vendor profile
    if request.user.role != 'VENDOR' or not hasattr(request.user, 'vendor_profile'):
        messages.error(request, "Unauthorized access. Only assigned vendors can submit quotations.")
        return redirect('rfq_list')
        
    vendor = request.user.vendor_profile
    rfq = get_object_or_404(RFQ, id=rfq_id, assigned_vendors=vendor)
    
    # Check if the bid submission deadline has passed
    if rfq.deadline < timezone.now():
        messages.error(request, "The submission window deadline for this RFQ has expired.")
        return redirect('rfq_list')
        
    # Retrieve existing quotation draft if it exists, enabling edit capabilities
    existing_quotation = Quotation.objects.filter(rfq=rfq, vendor=vendor).first()
    
    if request.method == 'POST':
        price_per_unit = request.POST.get('price_per_unit')
        delivery_timeline = request.POST.get('delivery_timeline')
        notes = request.POST.get('notes')
        
        try:
            # Backend total calculation logic execution
            calculated_total = float(price_per_unit) * int(rfq.quantity)
            
            if existing_quotation:
                # Update existing record (Editable Quotations functionality)
                existing_quotation.price_per_unit = price_per_unit
                existing_quotation.total_price = calculated_total
                existing_quotation.delivery_timeline_days = delivery_timeline
                existing_quotation.notes = notes
                existing_quotation.status = 'SUBMITTED'
                existing_quotation.save()
                messages.success(request, "Your quotation proposal has been modified and re-submitted.")
            else:
                # Create brand new proposal log entry
                Quotation.objects.create(
                    rfq=rfq,
                    vendor=vendor,
                    price_per_unit=price_per_unit,
                    total_price=calculated_total,
                    delivery_timeline_days=delivery_timeline,
                    notes=notes,
                    status='SUBMITTED'
                )
                messages.success(request, "Quotation successfully submitted for review.")
                
            return redirect('rfq_list')
            
        except (ValueError, TypeError) as e:
            messages.error(request, f"Validation failure: Ensure numeric parameters are formatted correctly. {str(e)}")

    context = {
        'rfq': rfq,
        'quotation': existing_quotation
    }
    return render(request, 'procurement/submit_quotation.html', context)