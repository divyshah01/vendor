# procurement/comparison_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Min
from .models import RFQ, Quotation

@login_required
def compare_quotations_view(request, rfq_id):
    # Enforce role-based access for procurement evaluation structures
    if request.user.role not in ['ADMIN', 'PROCUREMENT_OFFICER', 'MANAGER']:
        messages.error(request, "Access denied. You do not have permissions to review vendor bids.")
        return redirect('dashboard')
        
    rfq = get_object_or_404(RFQ, id=rfq_id)
    
    # Extract sorting criteria parameters
    sort_by = request.get_full_path_info().split('sort=')[-1].split('&')[0] if 'sort=' in request.get_full_path_info() else 'price'
    
    # Query all active submitted proposals for this specific RFQ
    quotations = Quotation.objects.filter(rfq=rfq, status='SUBMITTED')
    
    # Determine minimum baseline cost to trigger lowest-price conditional highlights
    lowest_price_calc = quotations.aggregate(Min('total_price'))['total_price__min']
    
    # Apply selected sorting logic matrix
    if sort_by == 'price':
        quotations = quotations.order_by('total_price')
    elif sort_by == 'timeline':
        quotations = quotations.order_by('delivery_timeline_days')
    elif sort_by == 'rating':
        quotations = quotations.order_by('-vendor__rating')

    context = {
        'rfq': rfq,
        'quotations': quotations,
        'lowest_price': lowest_price_calc,
        'current_sort': sort_by,
    }
    return render(request, 'procurement/compare_quotations.html', context)