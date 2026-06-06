from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('PROCUREMENT_OFFICER', 'Procurement Officer'),
        ('MANAGER', 'Manager / Approver'),
        ('VENDOR', 'Vendor'),
    )
    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default='PROCUREMENT_OFFICER')
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Vendor(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('PENDING', 'Pending Approval'),
        ('INACTIVE', 'Inactive'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile', null=True, blank=True)
    company_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)  # e.g., Hardware, Software, Services
    gst_number = models.CharField(max_length=15, unique=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)  # Vendor performance rating
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name