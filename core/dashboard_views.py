# core/dashboard_views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from procurement.models import RFQ, Quotation, ApprovalWorkflow, PurchaseOrder, Invoice

@login_required
def dashboard_view(request):
    user = request.user
    context = {
        'role': user.role,
        'pending_approvals_count': 0,
        'active_rfqs_count': 0,
        'recent_pos_count': 0,
        'recent_invoices_count': 0,
    }

    # Aggregate counts based on roles to populate analytics cards
    if user.role == 'ADMIN' or user.role == 'PROCUREMENT_OFFICER':
        context['active_rfqs_count'] = RFQ.objects.filter(status='OPEN').count()
        context['pending_approvals_count'] = ApprovalWorkflow.objects.filter(status='PENDING').count()
        context['recent_pos'] = PurchaseOrder.objects.all().order_index('-issued_date')[:5] if hasattr(PurchaseOrder.objects, 'order_index') else PurchaseOrder.objects.all().order_by('-issued_date')[:5]
        context['recent_invoices'] = Invoice.objects.all().order_index('-generated_at')[:5] if hasattr(Invoice.objects, 'order_index') else Invoice.objects.all().order_by('-generated_at')[:5]
        
    elif user.role == 'MANAGER':
        context['pending_approvals_count'] = ApprovalWorkflow.objects.filter(status='PENDING', approver=user).count()
        context['active_rfqs_count'] = RFQ.objects.filter(status='OPEN').count()
        context['recent_pos'] = PurchaseOrder.objects.all().order_index('-issued_date')[:5] if hasattr(PurchaseOrder.objects, 'order_index') else PurchaseOrder.objects.all().order_by('-issued_date')[:5]

    elif user.role == 'VENDOR':
        if hasattr(user, 'vendor_profile'):
            vendor = user.vendor_profile
            context['active_rfqs_count'] = RFQ.objects.filter(assigned_vendors=vendor, status='OPEN').count()
            context['recent_pos'] = PurchaseOrder.objects.filter(quotation__vendor=vendor).order_index('-issued_date')[:5] if hasattr(PurchaseOrder.objects, 'order_index') else PurchaseOrder.objects.filter(quotation__vendor=vendor).order_by('-issued_date')[:5]
            context['recent_invoices'] = Invoice.objects.filter(purchase_order__quotation__vendor=vendor).order_index('-generated_at')[:5] if hasattr(Invoice.objects, 'order_index') else Invoice.objects.filter(purchase_order__quotation__vendor=vendor).order_by('-generated_at')[:5]

    return render(request, 'dashboard/index.html', context)