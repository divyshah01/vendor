from .views import rfq_list_view, create_rfq_view
from django.urls import path
from .comparison_views import compare_quotations_view
from .quotation_views import submit_quotation_view
from .approval_views import initiate_approval_view, approval_queue_view, execute_approval_action_view
from .log_views import activity_logs_dashboard_view
from .document_views import document_management_center_view, generate_purchase_order_view, view_invoice_details_view
from .analytics_views import analytics_dashboard_view, export_csv_report_stub_view
urlpatterns = [
    path('rfqs/', rfq_list_view, name='rfq_list'),
    path('rfqs/create/', create_rfq_view, name='create_rfq'),
    path('rfqs/<int:rfq_id>/quote/', submit_quotation_view, name='submit_quotation'),
    path('rfqs/<int:rfq_id>/compare/', compare_quotations_view, name='compare_quotations'),
    path('approvals/initiate/', initiate_approval_view, name='initiate_approval'),
    path('approvals/queue/', approval_queue_view, name='approval_queue'),
    path('approvals/<int:workflow_id>/action/', execute_approval_action_view, name='execute_approval'),
    path('documents/', document_management_center_view, name='document_center'),
    path('documents/generate-po/<int:quotation_id>/', generate_purchase_order_view, name='generate_po'),
    path('documents/invoice/<int:invoice_id>/', view_invoice_details_view, name='view_invoice'),
    path('audit/logs/', activity_logs_dashboard_view, name='activity_logs'),
    path('management/analytics/', analytics_dashboard_view, name='analytics_dashboard'),
    path('management/analytics/export/', export_csv_report_stub_view, name='export_report'),
]
