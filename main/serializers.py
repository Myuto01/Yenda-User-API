# serializers.py
from rest_framework import serializers
from main.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
from django.contrib.auth import  authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)

class UserRegistrationSerializer(serializers.ModelSerializer):
   
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "password2"
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'error_messages': {'required': 'Password is required'}},
            'email': {'error_messages': {'unique': 'Email is already taken'}},
            'phone_number': {'error_messages': {'unique': 'phone_number is already taken'}}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': "Passwords do not match"})
        return data


class UserLoginSerializer(serializers.Serializer):
        phone_number = serializers.CharField()
        password = serializers.CharField(write_only=True, style={'input_type': 'password'})  # Set write_only=True and specify input_type
        full_name = serializers.CharField(read_only=True) 
        email = serializers.EmailField(read_only=True)
        access_token = serializers.CharField(read_only=True)  # Mark as read-only
        refresh_token = serializers.CharField(read_only=True)  # Mark as read-only

        class Meta:
            model = User
            fields = ['phone_number', 'password']   

        
        def validate(self, attrs):
            phone_number = attrs.get('phone_number')
            password = attrs.get('password')
            request = self.context.get('request')
            user = authenticate(request, phone_number=phone_number, password=password)
            print ('Authenticated')
            if not user:
                raise AuthenticationFailed("Invalid credential try again")
        
            user_tokens = user.tokens()

            access_token = user_tokens.get('access')

            return {
            'phone_number': user.phone_number,
            'full_name': user.get_full_name if hasattr(user, 'get_full_name') else '', 
            'phone_number': user.phone_number,
            'access_token': user_tokens.get('access'),
            'refresh_token': user_tokens.get('refresh')
        }

class UserDetailsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name' ,'phone_number']


class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = [
            "password",
            "password2" 
        ]

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            raise serializers.ValidationError("Passwords do not match")

        return data

class OTPVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=5)