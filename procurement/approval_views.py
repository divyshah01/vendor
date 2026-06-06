# procurement/approval_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Quotation, ApprovalWorkflow, ActivityLog

@login_required
def initiate_approval_view(request):
    if request.user.role not in ['ADMIN', 'PROCUREMENT_OFFICER']:
        messages.error(request, "Unauthorized operation framework access.")
        return redirect('rfq_list')

    if request.method == 'POST':
        quotation_id = request.POST.get('quotation_id')
        quotation = get_object_or_404(Quotation, id=quotation_id)
        
        # Prevent duplicate entries
        workflow, created = ApprovalWorkflow.objects.get_or_create(
            quotation=quotation,
            defaults={'status': 'PENDING'}
        )
        
        if created:
            quotation.status = 'UNDER_REVIEW'
            quotation.save()
            ActivityLog.objects.create(
                user=request.user,
                action=f"Initiated approval routing for Quotation #{quotation.id} ({quotation.vendor.company_name})"
            )
            messages.success(request, "Quotation submitted to the management approval tracking layout queue.")
        else:
            messages.info(request, "An active workflow tracking structure already exists for this quotation.")
            
    return redirect('approval_queue')


@login_required
def approval_queue_view(request):
    user = request.user
    if user.role not in ['ADMIN', 'MANAGER']:
        messages.error(request, "Access denied to executive verification logs.")
        return redirect('dashboard')

    # Managers only see items pending their action, Admins see the entire lifecycle matrix
    if user.role == 'MANAGER':
        workflows = ApprovalWorkflow.objects.filter(status='PENDING').order_by('-updated_at')
    else:
        workflows = ApprovalWorkflow.objects.all().order_by('-updated_at')

    return render(request, 'procurement/approval_queue.html', {'workflows': workflows})


@login_required
def execute_approval_action_view(request, workflow_id):
    if request.user.role not in ['ADMIN', 'MANAGER']:
        messages.error(request, "Unauthorized to execute workflow state changes.")
        return redirect('approval_queue')

    workflow = get_object_or_404(ApprovalWorkflow, id=workflow_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')  # APPROVED or REJECTED
        remarks = request.POST.get('remarks', '')

        if action in ['APPROVED', 'REJECTED']:
            workflow.status = action
            workflow.approver = request.user
            workflow.remarks = remarks
            workflow.save()

            # Synchronize status changes back down into the parent Quotation record
            quotation = workflow.quotation
            quotation.status = 'ACCEPTED' if action == 'APPROVED' else 'REJECTED'
            quotation.save()

            # Log history footprint trace
            ActivityLog.objects.create(
                user=request.user,
                action=f"Workflow state transition changed: {action} on Quote #{quotation.id}. Remarks: {remarks}"
            )
            messages.success(request, f"Workflow routed successfully. Transition finalized as: {action}.")
            
    return redirect('approval_queue')