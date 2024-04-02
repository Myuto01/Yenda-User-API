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
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "password2"
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'error_messages': {'required': 'Password is required'}},
            'email': {'error_messages': {'unique': 'Email is already taken'}},
            'username': {'error_messages': {'unique': 'Username is already taken'}}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': "Passwords do not match"})
        return data

    def save(self):
        password = self.validated_data['password']
        account = User.objects.create(
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            username=self.validated_data['username'],
            email=self.validated_data['email']
        )
        account.set_password(password)
        account.save()
        return account

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})  # Set write_only=True and specify input_type
    full_name = serializers.CharField(read_only=True) 
    email = serializers.EmailField(read_only=True)
    access_token = serializers.CharField(read_only=True)  # Mark as read-only
    refresh_token = serializers.CharField(read_only=True)  # Mark as read-only

    class Meta:
        model = User
        fields = ['username', 'password']   

    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        request = self.context.get('request')
        user = authenticate(request, username=username, password=password)
        print ('Authenticated')
        if not user:
            raise AuthenticationFailed("Invalid credential try again")
       
        user_tokens = user.tokens()

        access_token = user_tokens.get('access')

        return {
            'username': user.username,
            'full_name': user.get_full_name if hasattr(user, 'get_full_name') else '', 
            'email': user.email,
            'access_token': user_tokens.get('access'),
            'refresh_token': user_tokens.get('refresh')
        }
            
        




class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


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

    