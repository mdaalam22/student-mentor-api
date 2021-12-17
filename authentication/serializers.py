from django.contrib.auth import tokens
from django.core.exceptions import ValidationError
from django.views import generic
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from .models import User
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import Util
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from email_validator import validate_email, EmailNotValidError
import phonenumbers




class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=60,min_length=8,write_only=True)

    class Meta:
        model = User
        fields = ['username','name','email','phone_number','image','password']

    def validate(self, attrs):
        email = attrs.get('email','')
        username = attrs.get('username','')
        name = attrs.get('name','')
        phone_number_str = attrs.get('phone_number','')

        if not (len(username)>5 and len(username)<=30 and username.isalnum()):
            raise serializers.ValidationError(
                'The username should only contain alphanumeric character and must be between 6 and 30 chars long'
            )

        if not name.replace(" ", "").isalpha():
            raise serializers.ValidationError('Please enter a valid name,Name should contain only alphabets')
            
        
        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            raise serializers.ValidationError('Email is not valid')
        try:
            phone_num = phonenumbers.parse(phone_number_str)
            if not phonenumbers.is_valid_number(phone_num):
                raise ValidationError("Phone number is not valid")
        except phonenumbers.NumberParseException:
            raise ValidationError("Phone number is not valid")


        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']



class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255,min_length=4)
    password = serializers.CharField(max_length=70,min_length=8,write_only=True)
    email = serializers.EmailField(max_length=255,min_length=10,read_only=True)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self,obj):
        user = User.objects.get(username=obj['username'])

        return {
            'access':user.tokens()['access'],
            'refresh':user.tokens()['refresh'],
        }

    class Meta:
        model = User
        fields = ['username','email','password','tokens']

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        filtered_user_by_username = User.objects.filter(username=username)
        user = auth.authenticate(username=username, password=password)

        if filtered_user_by_username.exists() and filtered_user_by_username[0].auth_provider != 'email':
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_username[0].auth_provider)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')

        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens
        }

        return super().validate(attrs)


class RequestPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=6)
    redirect_url = serializers.CharField(max_length=500,required=False)

    class Meta:
        fields = ['email']


class setNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8,max_length=68,write_only=True)
    uidb64 = serializers.CharField(min_length=1,write_only=True)
    token = serializers.CharField(min_length=1,write_only=True)

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                raise AuthenticationFailed('The reset link is invalid',401)
            
            user.set_password(password)
            user.save()
            return user
        except:
            raise AuthenticationFailed('The reset link is invalid',401)

        return super().validate(attrs)



class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh')
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True,min_length=8)
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):

        user = self.context['request'].user

        if user.pk != instance.pk:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})

        instance.set_password(validated_data['password'])
        instance.save()

        return instance

class UpdateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'name', 'email','phone_number','image')

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(id=user.id).filter(email=value).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})
        try:
            valid = validate_email(value)
            email = valid.email
        except EmailNotValidError as e:
            raise serializers.ValidationError('Email is not valid')
        
        return value

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(id=user.id).filter(username=value).exists():
            raise serializers.ValidationError({"username": "This username is already in use."})

        if not (len(value)>5 and len(value)<=30 and value.isalnum()):
            raise serializers.ValidationError(
                'The username should only contain alphanumeric character and must be between 6 and 30 chars long'
            )
        return value

    def validate_name(self,value):
        if not value.replace(" ", "").isalpha():
            raise serializers.ValidationError('Please enter a valid name,Name should contain only alphabets')
        return value
    
    def validate_phone_number(self,value):
        try:
            phone_num = phonenumbers.parse(value)
            if not phonenumbers.is_valid_number(phone_num):
                raise ValidationError("Phone number is not valid")
        except phonenumbers.NumberParseException:
            raise ValidationError("Phone number is not valid")

        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.id != instance.id:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})

        instance.name = validated_data['name']
        instance.phone_number = validated_data['phone_number']
        instance.image = validated_data['image']
        instance.email = validated_data['email']
        instance.username = validated_data['username']

        instance.save()

        return instance