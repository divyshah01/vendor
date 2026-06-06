from django.db import models

# Create your models here.
# procurement/models.py
from django.db import models
from django.conf import settings
from core.models import Vendor

class RFQ(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('OPEN', 'Open (Accepting Bids)'),
        ('CLOSED', 'Closed'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    product_details = models.TextField()
    quantity = models.PositiveIntegerField()
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_rfqs')
    assigned_vendors = models.ManyToManyField(Vendor, related_name='assigned_rfqs')
    attachments = models.FileField(upload_to='rfq_attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Quotation(models.Model):
    STATUS_CHOICES = (
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    )
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name='quotations')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='quotations')
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)
    delivery_timeline_days = models.PositiveIntegerField(help_text="Estimated delivery time in days")
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quote from {self.vendor.company_name} for {self.rfq.title}"


class ApprovalWorkflow(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Manager Action'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='approvals')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'MANAGER'})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    remarks = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class PurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('ISSUED', 'Issued'),
        ('CANCELLED', 'Cancelled'),
    )
    po_number = models.CharField(max_length=50, unique=True)  # Auto-generated unique string
    quotation = models.OneToOneField(Quotation, on_delete=models.CASCADE, related_name='purchase_order')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    issued_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ISSUED')

    def __str__(self):
        return self.po_number


class Invoice(models.Model):
    STATUS_CHOICES = (
        ('UNPAID', 'Unpaid'),
        ('PAID', 'Paid'),
    )
    purchase_order = models.OneToOneField(PurchaseOrder, on_delete=models.CASCADE, related_name='invoice')
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2)  # Calculated from GST fields
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UNPAID')
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"INV-{self.purchase_order.po_number}"


class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} @ {self.timestamp}"