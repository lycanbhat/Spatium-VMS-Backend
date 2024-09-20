
from rest_framework import serializers

from admin_panel.models import Company, PurposeOfVisit
from authentication.models import CustomUser

from spatiumvms.constants import (
    EMAIL_LOGO,
    VISITOR_WAITING,
    DOWNLOAD_ID
)

from .models import Visitor
import re
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from spatiumvms.utils.brevo_utils import send_brevo_email

class VisitorSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    user_name = serializers.SerializerMethodField()
    purpose_of_visit_name = serializers.CharField(source='purpose_of_visit.name', read_only=True)
    phone_number = serializers.CharField(required=True)

    company_id = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), write_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), write_only=True)
    purpose_of_visit_id = serializers.PrimaryKeyRelatedField(queryset=PurposeOfVisit.objects.all(), write_only=True)

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else None
    
    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email cannot be empty")
        return value

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Phone number cannot be empty")
        if not re.match(r'^[0-9]{10}$', value):
            raise serializers.ValidationError("Invalid phone number format")
        return value

    def validate(self, data):
        self.validate_phone_number(data.get('phone_number'))
        return data

    def create(self, validated_data):
        company_id = validated_data.pop('company_id').id
        user_id = validated_data.pop('user_id').id
        purpose_of_visit_id = validated_data.pop('purpose_of_visit_id').id

        visitor = Visitor.objects.create(company_id=company_id, user_id=user_id, purpose_of_visit_id=purpose_of_visit_id, **validated_data)

        recipient = visitor.user.email
        subject = VISITOR_WAITING.get("subject", "")

        html_content = render_to_string('Visitor_request.html', {'employee_name':visitor.user.first_name,'name': visitor.name,'phone_number': visitor.phone_number,'email': visitor.email,'purpose_of_visit':visitor.purpose_of_visit.name , 'logo': EMAIL_LOGO,'from_company':visitor.from_company})

        to_emails = [recipient]
        
        success, message = send_brevo_email(subject, html_content, to_emails)


        visitor_recipient = visitor.email
        visitor_subject = DOWNLOAD_ID.get("subject", "")

        base_url = settings.FRONT_DOMAIN

        visitor_html_content = render_to_string('Download_id.html', {'name': visitor.name,'visitor_id':visitor.id,'base_url':base_url, 'logo': EMAIL_LOGO})

        visitor_to_emails = [visitor_recipient]
        
        success, message = send_brevo_email(visitor_subject, visitor_html_content, visitor_to_emails)
        
        return visitor

    class Meta:
        model = Visitor
        fields = ['id', 'email', 'phone_number', 'name', 'company_name', 'from_company', 'user_name', 'purpose_of_visit_id', 'purpose_of_visit_name', 'image', 'created_at', 'modified_at', 'company_id', 'user_id']
