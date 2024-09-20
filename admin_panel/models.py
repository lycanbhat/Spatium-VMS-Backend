from django.db import models

# Create your models here.
    
class PurposeOfVisit(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    is_archive = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    is_archive = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='state_city', null=True, blank=True)
    is_archive = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Zone(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='zone_city', null=True, blank=True)
    is_archive = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Facility(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='facility_city', null=True, blank=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='facility_zone', null=True, blank=True)
    address = models.TextField(blank=True)
    is_archive = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Company(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(blank=True)  # Changed to TextField
    logo = models.ImageField(upload_to='company_logo/', blank=True, max_length=4096)
    spoc_name = models.CharField(max_length=255, blank=True)
    spoc_email = models.EmailField(verbose_name='spoc_email', max_length=255, unique=True)
    spoc_phone_number = models.CharField(blank=True, max_length=13, unique=True)
    gstin = models.CharField(blank=True, max_length=255)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='company_facility', null=True, blank=True)
    is_archive = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name