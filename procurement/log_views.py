# procurement/log_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ActivityLog

@login_required
def activity_logs_dashboard_view(request):
    # Admins and Managers have visibility across all systemic change events.
    # Procurement Officers can look across general trends, while Vendors remain bound to their specific footprint.
    user = request.user
    
    if user.role in ['ADMIN', 'MANAGER', 'PROCUREMENT_OFFICER']:
        logs = ActivityLog.objects.all().order_by('-timestamp')
    else:
        # Filter log profiles directly correlated with actions containing the Vendor's account username signature context
        logs = ActivityLog.objects.filter(user=user).order_by('-timestamp')

    # Quick interactive keyword search filter layer
    search_keyword = request.GET.get('search_log', '')
    if search_keyword:
        logs = logs.filter(action__icontains=search_keyword)

    return render(request, 'procurement/activity_logs.html', {
        'logs': logs,
        'search_keyword': search_keyword
    })