from datetime import datetime, timedelta
import pytz
import io
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
import requests
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from admin_panel.models import Company
from authentication.models import CustomUser
from vms.models import Visitor
from vms.serializers import VisitorSerializer
from django.db.models import Prefetch
import qrcode
import cairosvg
import base64
import os

# Create your views here.


class CustomPagination(PageNumberPagination):

    def get_page_size(self, request):
        """
        Dynamically determine the page size.
        """
        # For example, you can get the page size from query parameter
        if 'page_size' in request.query_params:
            try:
                page_size = int(request.query_params['page_size'])
                if page_size > 0:
                    return page_size
            except ValueError:
                pass  # Fall back to the default page size if query parameter is invalid
        
        # Return the default page size if no query parameter is provided or invalid
        return self.page_size

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })

class VisitorView(viewsets.ModelViewSet):

    view_permissions = {
        'list': {'front_desk': True, 'admin' : True,'facility_manager': True},
        'create': {'front_desk': True, 'admin' : True,'facility_manager': True},
    }

    serializer_class=VisitorSerializer
    pagination_class = CustomPagination

    def list(self, request):
        
        is_superuser = self.request.user.is_superuser
        if is_superuser:
            queryset = Visitor.objects.prefetch_related(
                Prefetch('company', queryset=Company.objects.only('name')),
                Prefetch('user', queryset=CustomUser.objects.only('first_name', 'last_name'))
            ).order_by('-pk')
        else:
            facility_id = self.request.user.facility_id
            queryset = Visitor.objects.filter(company__facility=facility_id).prefetch_related(
                Prefetch('company', queryset=Company.objects.only('name')),
                Prefetch('user', queryset=CustomUser.objects.only('first_name', 'last_name'))
            ).order_by('-pk')
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class QRCodeView(viewsets.ViewSet):
    view_permissions = {
        'create': {'front_desk': True, 'admin' : True},
    }

    def create(self, request, *args, **kwargs):
        visitor_id = request.data.get('visitor_id')
        
        # Create a QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        # Add the URL to the QR code
        qr.add_data(settings.FRONT_DOMAIN+"/api/v1/vms/identity-card/?visitor_id="+visitor_id)
        qr.make(fit=True)

        # Create an image from the QR code
        img = qr.make_image(fill_color="black", back_color="white")

        # Define the path to save the image
        image_path = os.path.join(settings.MEDIA_ROOT, 'qrcodes', f'qrcode_{visitor_id}.png')

        # Save the image to the local file system
        img.save(image_path)

        # Generate the URL for accessing the saved image
        image_url = os.path.join(settings.MEDIA_URL, 'qrcodes', f'qrcode_{visitor_id}.png')

        # Return the URL
        return Response({'url': settings.FRONT_DOMAIN+ image_url})
    
class IdentityCardView(viewsets.ViewSet):
    view_permissions = {
        'list': {'anon': True},
    }

    def list(self, request, *args, **kwargs):


        # Retrieve the visitor_id from the request query parameters
        visitor_id = request.query_params.get('visitor_id')

        visitor = Visitor.objects.select_related('company').prefetch_related(
                    Prefetch('user', queryset=CustomUser.objects.only('first_name', 'last_name'))
                ).filter(id=visitor_id).values('name', 'image', 'phone_number', 'created_at', 'purpose_of_visit__name', 'company__name', 'user__first_name', 'user__last_name').first()
        
        if not visitor:
            return Response(
                { "error": "Visitor is not found." }, status=status.HTTP_404_NOT_FOUND
            )

        else:
            # Get the name from the visitor object
            name = visitor['name']
            phone_number = visitor['phone_number']
            image = visitor['image']
            purpose_of_visit = visitor['purpose_of_visit__name']
            company_name = visitor['company__name']
            created_at = visitor['created_at']
            formatted_created_at = created_at.strftime("%d %b %Y")
            user_name = f"{visitor['user__first_name']} {visitor['user__last_name']}"

            # Assuming created_at is already a datetime object in UTC
            created_at_utc = visitor['created_at'].replace(tzinfo=pytz.UTC)

            # Convert the UTC time to the appropriate time zone (+0530)
            local_timezone = pytz.timezone('Asia/Kolkata')
            created_at_local = created_at_utc.astimezone(local_timezone)

            # Add three hours
            new_time_local = created_at_local + timedelta(hours=3)

            # If the new time is on the next day, set the end date to the current day, 11:59 PM
            if new_time_local.date() > created_at_local.date():
                end_date = created_at_local.replace(hour=23, minute=59, second=59)
            else:
                end_date = new_time_local

            # Format the end date as "Hour:Minute AM/PM"
            formatted_end_date = end_date.strftime('%I:%M %p')

            # URL of the image
            image_url = "https://spatiumoffices.com/wp-content/uploads/2024/03/spatium-logo-white.png"

            # Fetch the image from the URL
            image_response = requests.get(image_url)

            # Fetch the image from the URL
            profile_image_response = requests.get(settings.FRONT_DOMAIN+'/media/'+str(image))

            # Check if the request was successful
            if image_response.status_code == 200:
                # Convert the image to base64
                base64_image = base64.b64encode(image_response.content).decode()

                base64_profile_image = base64.b64encode(profile_image_response.content).decode()

                # Update the SVG content with the base64-encoded image data
                svg_content = f"""<?xml version="1.0" encoding="utf-8"?>
                                <!-- Generator: Adobe Illustrator 28.3.0, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
                                <svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
                                    viewBox="0 0 1125 1963" style="enable-background:new 0 0 1125 1963;" xml:space="preserve">
                                <g>
                                    
                                        <linearGradient id="Rectangle_15_00000061439451003741594480000011590328598646312856_" gradientUnits="userSpaceOnUse" x1="0.793" y1="2438.2202" x2="0.793" y2="2435.219" gradientTransform="matrix(375 0 0 -654 265 1594596)">
                                        <stop  offset="0" style="stop-color:#6E36C5"/>
                                        <stop  offset="0.429" style="stop-color:#411F74"/>
                                        <stop  offset="1" style="stop-color:#2F1754"/>
                                    </linearGradient>
                                    
                                        <rect id="Rectangle_15" x="-0.34" y="0" style="fill:url(#Rectangle_15_00000061439451003741594480000011590328598646312856_);" width="1125.46" height="1962.81"/>
                                    <g id="Rectangle_14" transform="translate(14 179)">
                                        <path style="opacity:0.1;fill:#FFFFFF;" d="M69.69,358.22h954.39c23.21,0,42.02,18.81,42.02,42.02v1293.53
                                            c0,23.21-18.81,42.02-42.02,42.02H69.69c-23.21,0-42.02-18.81-42.02-42.02V400.24C27.67,377.03,46.48,358.22,69.69,358.22z"/>
                                        <path style="fill:none;stroke:#FFFFFF;" d="M69.69,359.72h954.39c22.38,0,40.52,18.14,40.52,40.52v1293.53
                                            c0,22.38-18.14,40.52-40.52,40.52H69.69c-22.38,0-40.52-18.14-40.52-40.52V400.24C29.17,377.86,47.31,359.72,69.69,359.72z"/>
                                    </g>
                                    <g id="Rectangle_13" transform="translate(128 120)">
                                        <path style="fill:#FFFFFF;" d="M282.82,240.15h300.12c14.92,0,27.01,12.09,27.01,27.01v300.12c0,14.92-12.09,27.01-27.01,27.01
                                            H282.82c-14.92,0-27.01-12.09-27.01-27.01V267.16C255.81,252.24,267.91,240.15,282.82,240.15z"/>
                                        <path style="fill:none;stroke:#FFFFFF;" d="M282.82,241.65h300.12c14.09,0,25.51,11.42,25.51,25.51v300.12
                                            c0,14.09-11.42,25.51-25.51,25.51H282.82c-14.09,0-25.51-11.42-25.51-25.51V267.16C257.31,253.07,268.74,241.65,282.82,241.65z"/>
                                    </g>
                                    
                                        <text transform="matrix(1 0 0 1 550 843.3472)" text-anchor="middle" style="fill:#FFFFFF; font-family:'IBMPlexSans-SemiBold'; font-size:78.0321px;">{name}</text>
                                    
                                        <text transform="matrix(1 0 0 1 550 939.3877)" text-anchor="middle" style="fill:#FFFFFF; font-family:'IBMPlexSans-Medium'; font-size:54.0222px;">{phone_number}</text>
                                    
                                        <text transform="matrix(1 0 0 1 344.7998 1134.4683)" style="fill:#FFFFFF; font-family:'IBMPlexSans-SemiBold'; font-size:78.0321px;">Host details</text>
                                    
                                        <text transform="matrix(1 0 0 1 550 1236.5098)" text-anchor="middle" style="fill:#FFFFFF; font-family:'IBMPlexSans-Medium'; font-size:60.0247px;">{company_name}</text>
                                    
                                        <text transform="matrix(1 0 0 1 550 1311.542)" text-anchor="middle" style="fill:#FFFFFF; font-family:'IBMPlexSans-Medium'; font-size:60.0247px;">{user_name}</text>
                                    
                                        <text transform="matrix(1 0 0 1 550 1467.6064)" text-anchor="middle" style="fill:#FFFFFF; font-family:'IBMPlexSans-SemiBold'; font-size:78.0321px;">{purpose_of_visit}</text>
                                    
                                        <text transform="matrix(1 0 0 1 191.7358 1617.6689)" style="fill:#FFFFFF; font-family:'IBMPlexSans-SemiBold'; font-size:48.0198px;">Valid till: {formatted_end_date} | {formatted_created_at}</text>
                                    
                                        <text transform="matrix(1 0 0 1 281.7734 1851.7646)" style="fill:#FFFFFF; font-family:'IBMPlexSans-SemiBold'; font-size:138.0568px;">VISITOR</text>
                                    <line id="Line_1" style="fill:none;stroke:#FFFFFF;" x1="43.17" y1="1000.91" x2="1078.6" y2="1000.91"/>
                                    <line id="Line_2" style="fill:none;stroke:#FFFFFF;" x1="43.17" y1="1691.2" x2="1078.6" y2="1691.2"/>
                                    <line id="Line_4" style="fill:none;stroke:#FFFFFF;" x1="43.17" y1="1509.62" x2="1078.6" y2="1509.62"/>
                                    <line id="Line_3" style="fill:none;stroke:#FFFFFF;" x1="43.17" y1="1379.07" x2="1078.6" y2="1379.07"/>
                                    
                                        <image style="overflow:visible;enable-background:new    ;" width="107" height="106" id="sample2" xlink:href="data:image/png;base64,{base64_profile_image}" transform="matrix(3.0012 0 0 3.0012 398.8195 378.1557)">
                                    </image>

                                    <image style="overflow:visible;enable-background:new ;" width="173" height="65" id="sample" xlink:href="data:image/png;base64,{base64_image}" transform="matrix(3.0012 0 0 3.0012 302.78 87.0358)">
                                    </image>
                                </g>
                                </svg>
                                """

                try:
                    # Convert SVG to PNG
                    png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))

                    # Return the PNG image as a response
                    response = HttpResponse(png_data, content_type='image/png')
                    response['Content-Disposition'] = 'attachment; filename="visitor_'+visitor_id+'.png"'
                    return response
                except Exception as e:
                    # Log any errors that occur during the conversion
                    print("Error during SVG to PNG conversion:", e)
                    return Response(
                        { "error": "Failed to convert SVG to PNG." }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                # If the request fails, return an error response
                return Response(
                    { "error": "Failed to fetch image." }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


class VMSDashboardView(viewsets.ModelViewSet):

    view_permissions = {
        'list': {'admin': True,'front_desk': True},
    }

    def list(self, request):
        
        facility_id = self.request.user.facility_id

        company_ids = Company.objects.filter(facility_id=facility_id).values_list('id', flat=True)
        
        # Get the current month and day
        current_month = datetime.now().month
        current_day = datetime.now().day
        
        # Count visitors for the current day
        visitors_today_count = Visitor.objects.filter(
            company_id__in=company_ids,
            created_at__year=datetime.now().year,
            created_at__month=current_month,
            created_at__day=current_day
        ).count()
        
        # Count visitors for the current month
        visitors_this_month_count = Visitor.objects.filter(
            company_id__in=company_ids,
            created_at__year=datetime.now().year,
            created_at__month=current_month
        ).count()
        
        return Response({
            'visitors_today_count': visitors_today_count,
            'visitors_this_month_count': visitors_this_month_count
        })
    
class CompanyVisitorView(viewsets.ModelViewSet):

    view_permissions = {
        'list': {'admin': True,'front_desk': True},
    }

    def list(self, request):
        
        
        company_id = request.query_params.get('company_id')

        
        # Get the current month and day
        current_month = datetime.now().month
        current_day = datetime.now().day
        
        # Count visitors for the current day
        visitors_count = Visitor.objects.filter(
            company_id__in=company_id,
            created_at__year=datetime.now().year,
            created_at__month=current_month,
            created_at__day=current_day
        ).count()

        return Response({
            'visitors_count': visitors_count
        })