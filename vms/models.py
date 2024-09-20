from django.db import models

from admin_panel.models import Company, PurposeOfVisit
from authentication.models import CustomUser

# Create your models here.

class Visitor(models.Model):
    email = models.EmailField(verbose_name='visitors_email', max_length=255, db_index=True)
    phone_number = models.CharField(blank=True, max_length=13, db_index=True)
    name = models.CharField(max_length=100, blank=True)
    from_company = models.TextField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='visitor_company', null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='visitor_user', null=True, blank=True)
    purpose_of_visit = models.ForeignKey(PurposeOfVisit, on_delete=models.CASCADE, related_name='purpose_if_visit', null=True, blank=True)
    image = models.ImageField(upload_to='visitors/', blank=True, max_length=4096)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name