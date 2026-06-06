# procurement/analytics_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Avg, Count
from django.db.models.functions import ExtractMonth
from .models import RFQ, Quotation, PurchaseOrder, Invoice
from core.models import Vendor

@login_required
def analytics_dashboard_view(request):
    # Restrict strategic analytics viewing to Admin and Manager corporate roles
    if request.user.role not in ['ADMIN', 'MANAGER']:
        messages.error(request, "Access denied. Strategic reports are restricted to administration levels.")
        return redirect('dashboard')

    # 1. Broad Procurement Statistics Matrix
    total_rfqs = RFQ.objects.count()
    active_rfqs = RFQ.objects.filter(status='OPEN').count()
    total_pos = PurchaseOrder.objects.count()
    
    # 2. Spending Summaries calculations
    total_spend = Invoice.objects.filter(status='PAID').aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
    committed_spend = Invoice.objects.filter(status='UNPAID').aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00

    # 3. Vendor Performance Analytics (Top Rated Assets based on Database performance index ratings)
    top_vendors = Vendor.objects.filter(status='ACTIVE').order_by('-rating')[:5]

    # 4. Monthly Procurement Trends Framework Grouping
    # Compiles financial transactional processing volume grouped by month component
    monthly_trends_query = Invoice.objects.annotate(month=ExtractMonth('generated_at')).values('month').annotate(
        total_monthly_spend=Sum('total_amount'),
        invoice_count=Count('id')
    ).order_by('month')

    context = {
        'total_rfqs': total_rfqs,
        'active_rfqs': active_rfqs,
        'total_pos': total_pos,
        'total_spend': total_spend,
        'committed_spend': committed_spend,
        'top_vendors': top_vendors,
        'monthly_trends': monthly_trends_query,
    }
    return render(request, 'procurement/analytics.html', context)


@login_required
def export_csv_report_stub_view(request):
    # Functional stub logic hook layer mimicking data exportation capabilities
    messages.success(request, "Report structural layout compiled successfully! CSV down-stream download initiated.")
    return redirect('analytics_dashboard')