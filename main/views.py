from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from json import JSONDecodeError
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserDetailsUpdateSerializer,
    PasswordChangeSerializer,
    OTPVerificationSerializer
)
from rest_framework.parsers import JSONParser
from rest_framework import views, status
from rest_framework.response import Response
from .validations import custom_validation, validate_username, validate_password
from django.contrib.auth import  authenticate, login, logout
from .models import User, Code
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import DjangoModelPermissions
from .permissions import AllowAnyPermission
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import generate_otp_for_user_from_session  


class RegistrationAPIView(APIView):

    permission_classes = [AllowAnyPermission]

    serializer_class = UserRegistrationSerializer

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)


    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Retrieve phone number from request data
            phone_number = request.data.get('phone_number')
            
            # Check if phone number already exists in the database
            if User.objects.filter(phone_number=phone_number).exists():
                return Response({'error': 'Phone number already registered'}, status=status.HTTP_400_BAD_REQUEST)

            # Store user data in the session
            user_data = serializer.validated_data
            request.session['temp_user_data'] = user_data
            request.session.save()
            
            # Generate OTP for the user using the user data
            otp_number = generate_otp_for_user_from_session(request)

            # Print all data stored in the session
            print("Session Data:", request.session.__dict__['_session_cache'])

            # Return a response with a success message and the OTP
            return Response({'message': 'Verification code sent. Please enter the code on the next page.', 'otp': otp_number}, status=status.HTTP_202_ACCEPTED)
        else:
            errors = serializer.errors
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            # Retrieve the OTP from the serializer data
            otp = serializer.validated_data['otp']

            # Retrieve the stored OTP from the session
            stored_otp = request.session.get('otp')

            # Compare the entered OTP with the stored OTP
            if stored_otp == otp:
                # OTP verification successful
                # Retrieve user data from the session
                user_data = request.session.get('temp_user_data')
                if not user_data:
                    return Response({'error': 'User data not found in session'}, status=status.HTTP_400_BAD_REQUEST)

                # Remove the 'password2' field from user data if present
                user_data.pop('password2', None)

                # Create the user with the provided data
                user = User.objects.create_user(**user_data)

                # Delete the temporary user data from the session
                del request.session['temp_user_data']
                del request.session['otp']
                request.session.clear()
                
                return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
            else:
                # Invalid OTP
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# log in test (comment out in production)
def login(request):
    context = {}
    return render(request, 'login.html', context)

def dashboard(request):
    context = {}
    return render(request, 'dashboard.html', context)

############################################################

class UserLogin(APIView):
    permission_classes = [AllowAnyPermission]

    def post(self, request):
        data = JSONParser().parse(request)
        # Validate request data using serializer
        serializer = UserLoginSerializer(data=data , context = {'request':request})
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UserDetailsUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        user = User.objects.get(pk=pk)
        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        user = User.objects.get(pk=pk)
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']
            user.set_password(password)
            user.save()
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

