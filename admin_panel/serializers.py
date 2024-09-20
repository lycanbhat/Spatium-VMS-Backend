
from rest_framework import serializers

from authentication.models import CustomRole, CustomUser
from vms.models import Visitor

from .models import City, Company, Facility, PurposeOfVisit, State, Zone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from spatiumvms.constants import (
    EMPTY_NAME_ERROR
)

class StateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    class Meta:
        model = State
        fields = '__all__'

    def validate_name(self, value):
        """
        Check if the name is not empty.
        """
        if not value.strip():
            raise serializers.ValidationError(EMPTY_NAME_ERROR)
        return value


class CitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())

    class Meta:
        model = City
        fields = '__all__'

    def validate_name(self, value):
        """
        Check if the name is not empty.
        """
        if not value.strip():
            raise serializers.ValidationError(EMPTY_NAME_ERROR)
        return value

    def validate_state(self, value):
        """
        Check if the state exists.
        """
        if not State.objects.filter(pk=value.pk).exists():
            raise serializers.ValidationError("Invalid state ID.")
        return value

class FacilitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    zone = serializers.PrimaryKeyRelatedField(queryset=Zone.objects.all())
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())

    class Meta:
        model = Facility
        fields = '__all__'

    def validate_name(self, value):
        """
        Check if the name is not empty.
        """
        if not value.strip():
            raise serializers.ValidationError(EMPTY_NAME_ERROR)
        return value
    
    def validate_city(self, value):
        """
        Check if the City exists.
        """
        if value is not None and not City.objects.filter(pk=value.pk).exists():
            raise serializers.ValidationError("Invalid City ID.")
        return value

    def validate_zone(self, value):
        """
        Check if the Zone exists.
        """
        if value is not None and not Zone.objects.filter(pk=value.pk).exists():
            raise serializers.ValidationError("Invalid Zone ID.")
        return value
    
class ZoneSerializer(serializers.ModelSerializer):

    name = serializers.CharField(required=True)

    class Meta:
        model = Zone
        fields = '__all__'

    def validate_name(self, value):
        """
        Check if the name is not empty.
        """
        if not value.strip():
            raise serializers.ValidationError(EMPTY_NAME_ERROR)
        return value
    
class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomRole
        fields = '__all__'

class CompanyVisitorSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    user_name = serializers.SerializerMethodField()
    purpose_of_visit_name = serializers.CharField(source='purpose_of_visit.name', read_only=True)

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else None

    class Meta:
        model = Visitor
        fields = ['id', 'email', 'phone_number', 'name', 'company_name', 'from_company', 'user_name', 'purpose_of_visit_id', 'purpose_of_visit_name', 'image', 'created_at', 'modified_at', 'company_id', 'user_id']

class CompanySerializer(serializers.ModelSerializer):

    name = serializers.CharField(required=True)
    gstin = serializers.CharField(required=True)
    facility = serializers.PrimaryKeyRelatedField(queryset=Facility.objects.all())
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = '__all__'

    def get_employee_count(self, obj):
        """
        Method to get the count of employees related to the company.
        """
        return CustomUser.objects.filter(company=obj).count()

    def validate_name(self, value):
        """
        Check if the name is not empty.
        """
        if not value.strip():
            raise serializers.ValidationError(EMPTY_NAME_ERROR)
        return value
    
    def validate_gstin(self, value):
        """
        Validate that the GSTIN is not empty or only whitespace.
        """
        if not value.strip():
            raise serializers.ValidationError("GSTIN cannot be empty.")
        return value
    
    def validate_facility(self, value):
        """
        Check if the facility exists.
        """
        if value is not None and not Facility.objects.filter(pk=value.pk).exists():
            raise serializers.ValidationError("Invalid Facility ID.")
        return value
    
class UserSerializer(serializers.ModelSerializer):

    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(required=False)
    role_id = serializers.IntegerField(required=False)
    company_id = serializers.IntegerField(required=False)
    facility_id = serializers.IntegerField(required=False)
    zone_id = serializers.IntegerField(required=False)

    class Meta:
        model = CustomUser
        fields = '__all__'

    def validate_email(self, value):
        # Validate email format using Django's built-in validator
        try:
            validate_email(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        # You may add additional custom validation here if needed
        
        return value

    def validate_phone_number(self, value):
        # Add custom validation for phone number
        # For example, you can check the format or uniqueness
        
        # Check if the phone number contains only digits
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        
        # Check if the phone number length is within a specific range
        if len(value) < 10 or len(value) > 13:
            raise serializers.ValidationError("Phone number must be between 10 and 13 characters.")
        
        # You may add more validation logic here
        
        return value
    
    def validate(self, data):
        # Add custom validation for the entire object if needed
        # For example, you might want to ensure that email and phone_number combination is unique
        email = data.get('email')
        phone_number = data.get('phone_number')

        if self.instance:
            # When updating, check if the existing combination belongs to another instance
            if CustomUser.objects.filter(email=email, phone_number=phone_number).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("This email and phone number combination already exists.")
        else:
            # When creating, ensure the combination is unique
            if CustomUser.objects.filter(email=email, phone_number=phone_number).exists():
                raise serializers.ValidationError("This email and phone number combination already exists.")
        return data
    
class PurposeOfVisitSerializer(serializers.ModelSerializer):

    name = serializers.CharField(required=True)

    class Meta:
        model = PurposeOfVisit
        fields = '__all__'

    def validate_name(self, value):
        """
        Check if the name is not empty.
        """
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        return value