# procurement/document_views.py
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Quotation, PurchaseOrder, Invoice, ActivityLog

@login_required
def document_management_center_view(request):
    if request.user.role not in ['ADMIN', 'PROCUREMENT_OFFICER']:
        messages.error(request, "Access denied to official financial document pipelines.")
        return redirect('dashboard')
        
    # Fetch quotations that have been approved but do not have a PO issued yet
    approvals_ready = Quotation.objects.filter(status='ACCEPTED', purchase_order__isnull=True)
    active_pos = PurchaseOrder.objects.all().order_by('-issued_date')
    
    context = {
        'approvals_ready': approvals_ready,
        'active_pos': active_pos
    }
    return render(request, 'procurement/document_center.html', context)


@login_required
def generate_purchase_order_view(request, quotation_id):
    if request.user.role not in ['ADMIN', 'PROCUREMENT_OFFICER']:
        messages.error(request, "Unauthorized to compile official purchasing documents.")
        return redirect('document_center')

    quote = get_object_or_404(Quotation, id=quotation_id, status='ACCEPTED')
    
    # Auto-generate a unique PO number token string
    unique_po_token = f"PO-{uuid.uuid4().hex[:8].upper()}"
    
    # Generate Purchase Order record
    po = PurchaseOrder.objects.create(
        po_number=unique_po_token,
        quotation=quote,
        created_by=request.user,
        status='ISSUED'
    )
    
    # Run structural tax calculation metrics (e.g., standard 18% structural GST application)
    subtotal = quote.total_price
    tax_rate = 0.18
    calculated_tax = subtotal * tax_rate
    grand_total = subtotal + calculated_tax
    
    # Generate matching downstream Invoice record automatically
    Invoice.objects.create(
        purchase_order=po,
        subtotal=subtotal,
        tax_amount=calculated_tax,
        total_amount=grand_total,
        status='UNPAID'
    )
    
    ActivityLog.objects.create(
        user=request.user,
        action=f"Compiled official PO: {unique_po_token} and Invoice tracking entries for Quote #{quote.id}."
    )
    
    messages.success(request, f"Purchase Order {unique_po_token} and corresponding Invoice compiled successfully.")
    return redirect('document_center')


@login_required
def view_invoice_details_view(request, invoice_id):
    # Allow buyers and the target winning vendor to review the compiled financial document sheet
    invoice = get_object_or_404(Invoice, id=invoice_id)
    vendor_profile = invoice.purchase_order.quotation.vendor
    
    if request.user.role == 'VENDOR' and request.user.vendor_profile != vendor_profile:
        messages.error(request, "Access denied. This invoice profile belongs to another external vendor.")
        return redirect('dashboard')
        
    return render(request, 'procurement/invoice_print_view.html', {'invoice': invoice})