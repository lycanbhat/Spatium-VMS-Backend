
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter

import os
import pandas as pd

from authentication.models import CustomRole, CustomUser
from vms.models import Visitor

from .models import Company, PurposeOfVisit, State, City, Facility, Zone
from .serializers import CompanySerializer, CompanyVisitorSerializer, PurposeOfVisitSerializer, RoleSerializer, StateSerializer, CitySerializer, FacilitySerializer, UserSerializer, ZoneSerializer
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
    
class StateView(viewsets.ModelViewSet):

    view_permissions = {
        'create': {'admin': True},
        'list': {'admin': True},
        'retrieve': {'admin': True},
        'update': {'admin': True},
        'destroy': {'admin': True},
    }

    queryset = State.objects.filter(is_archive = False).order_by('pk')
    serializer_class=StateSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_archive = True  # Assuming you have an 'is_archived' field in your model
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CityView(viewsets.ModelViewSet):

    view_permissions = {
        'create': {'admin': True},
        'list': {'admin': True},
        'retrieve': {'admin': True},
        'update': {'admin': True},
        'destroy': {'admin': True},
    }

    queryset = City.objects.filter(is_archive = False).order_by('pk')
    serializer_class=CitySerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_archive = True  # Assuming you have an 'is_archived' field in your model
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FacilityView(viewsets.ModelViewSet):

    view_permissions = {
        'create': {'admin': True},
        'list': {'admin': True},
        'retrieve': {'admin': True},
        'update': {'admin': True},
        'destroy': {'admin': True},
    }

    queryset = Facility.objects.filter(is_archive = False).order_by('pk')
    serializer_class=FacilitySerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_archive = True  # Assuming you have an 'is_archived' field in your model
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class RoleView(viewsets.ModelViewSet):

    view_permissions = {
        'list': {'admin': True},
    }

    serializer_class=RoleSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    pagination_class = CustomPagination

    def get_queryset(self):

        if self.request.user.is_superuser:
            return CustomRole.objects.filter().order_by('priority')
        else:
            role_id = self.request.user.role.priority
            return CustomRole.objects.filter(priority__gte=role_id).order_by('priority')
            
class ZoneView(viewsets.ModelViewSet):

    view_permissions = {
        'create': {'admin': True},
        'list': {'admin': True},
        'retrieve': {'admin': True},
        'update': {'admin': True},
        'destroy': {'admin': True},
    }

    queryset = Zone.objects.filter(is_archive = False).order_by('pk')
    serializer_class=ZoneSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_archive = True  # Assuming you have an 'is_archived' field in your model
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CompanyView(viewsets.ModelViewSet):

    view_permissions = {
        'list': {'admin': True,'front_desk': True},
        'create': {'admin': True},
        'retrieve': {'admin': True},
        'update': {'admin': True},
        'destroy': {'admin': True},
    }

    serializer_class=CompanySerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    pagination_class = CustomPagination

    def get_queryset(self):
        # Retrieve the visitor_id from the request query parameters
        return Company.objects.filter(is_archive=False).order_by('pk')
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            company = serializer.save()

            try:
                user = CustomUser.objects.create(
                    first_name=request.data.get('spoc_name'),
                    email=request.data.get('spoc_email'),
                    phone_number=request.data.get('spoc_phone_number'),
                    role_id=4,
                    facility=Facility.objects.get(id=request.data.get('facility')),
                    company=company,
                    zone=None,
                    is_staff=False,
                    profile_picture=None
                )
                user.set_password("12345678")  # Set a default password or generate one
                user.save()
            except Exception as e:
                company.delete()  # Rollback company creation if user creation fails
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_archive = True  # Assuming you have an 'is_archived' field in your model
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CompanyUserView(viewsets.ModelViewSet):

    view_permissions = {
        'list': {'admin': True,'front_desk': True}
    }
    
    serializer_class=UserSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        # Retrieve the visitor_id from the request query parameters
        company_id = self.request.query_params.get('company_id')
        return CustomUser.objects.filter(is_archive=False, company_id=company_id).order_by('pk')
    
class CompanyVisitorView(viewsets.ModelViewSet):

    view_permissions = {
        'list': {'spoc': True}
    }
    
    serializer_class=CompanyVisitorSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        # Retrieve the visitor_id from the request query parameters
        company_id = self.request.query_params.get('company_id')
        return Visitor.objects.filter(company_id=company_id).order_by('pk')
    

class EmployeesView(viewsets.ModelViewSet):

    view_permissions = {
        'list': {'admin': True,'spoc': True},
        'create': {'admin': True,'spoc': True},
        'retrieve': {'admin': True,'spoc': True},
        'update': {'admin': True,'spoc': True},
        'destroy': {'admin': True,'spoc': True},
    }
    
    serializer_class=UserSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        # Retrieve the visitor_id from the request query parameters
        company_id = self.request.query_params.get('company_id')
        return CustomUser.objects.filter(is_archive=False, role_id__in=[4, 5], company_id=company_id).order_by('pk')
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_archive = True  # Assuming you have an 'is_archived' field in your model
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
class UsersView(viewsets.ModelViewSet):

    view_permissions = {
        'create': {'admin': True},
        'list': {'admin': True},
        'retrieve': {'admin': True},
        'update': {'admin': True},
        'destroy': {'admin': True},
    }

    queryset = CustomUser.objects.filter(is_archive = False).order_by('pk')
    serializer_class=UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ['first_name','last_name','email']
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_archive = True  # Assuming you have an 'is_archived' field in your model
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class PurposeOfVisitView(viewsets.ModelViewSet):

    view_permissions = {
        'create': {'admin': True},
        'list': {'admin': True,'front_desk': True},
        'retrieve': {'admin': True},
        'update': {'admin': True},
        'destroy': {'admin': True},
    }

    queryset = PurposeOfVisit.objects.filter(is_archive = False).order_by('pk')
    serializer_class=PurposeOfVisitSerializer
    pagination_class = CustomPagination


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_archive = True  # Assuming you have an 'is_archived' field in your model
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class BulkEmployeeUploadView(viewsets.ViewSet):

    view_permissions = {
        'create': {'admin': True,'spoc': True}
    }

    def create(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        role_id=request.data.get('role_id')
        company_id=request.data.get('company_id')

        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        file_ext = os.path.splitext(file.name)[1].lower()
        valid_extensions = ['.csv']

        if file_ext not in valid_extensions:
            return Response({'error': 'Invalid file format'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file)

            # Validate column names
            required_columns = ['FirstName', 'LastName', 'PhoneNumber', 'Email']
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                return Response({'error': f'Missing required columns: {list(missing_columns)}'}, status=status.HTTP_400_BAD_REQUEST)

            # Track success and failure counts
            success_count = 0
            failure_count = 0
            failure_reasons = []

            for index, row in df.iterrows():
                first_name = row['FirstName']
                last_name = row['LastName']
                phone_number = row['PhoneNumber']
                email = row['Email']

                # Check if user with email or phone number already exists
                if CustomUser.objects.filter(email=email).exists():
                    failure_count += 1
                    failure_reasons.append(f"Row {index+1}: Email '{email}' already exists.")
                    continue

                if CustomUser.objects.filter(phone_number=phone_number).exists():
                    failure_count += 1
                    failure_reasons.append(f"Row {index+1}: Phone number '{phone_number}' already exists.")
                    continue

                # Create new user
                try:
                    CustomUser.objects.create(email=email, phone_number=phone_number, first_name=first_name, last_name=last_name, company_id=company_id, role_id=role_id,is_staff=False)
                    success_count += 1
                except Exception as e:
                    failure_count += 1
                    failure_reasons.append(f"Row {index+1}: Failed to add user '{email}' due to error: {str(e)}")

            response_data = {
                "message": "Bulk upload completed.",
                "success_count": success_count,
                "failure_count": failure_count,
                "failures": failure_reasons
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except pd.errors.EmptyDataError:
            return Response({'error': 'Empty file provided'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)