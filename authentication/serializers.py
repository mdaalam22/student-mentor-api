from django.contrib.auth import tokens
from django.core.exceptions import ValidationError
from django.db.models import fields
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

from django.contrib.auth import password_validation as pass_validator
from django.core import exceptions
import datetime


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =  ['username','name','email','phone_number','image','dob','institute','address']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=60,min_length=8,write_only=True)

    class Meta:
        model = User
        fields = ['username','name','email','phone_number','image','dob','institute','address','password']

    def validate(self, attrs):
        email = attrs.get('email','')
        username = attrs.get('username','')
        name = attrs.get('name','')
        phone_number_str = attrs.get('phone_number','')
        password = attrs.get('password','')
        dob = attrs.get('dob','')
        institute = attrs.get('institute','')
        address = attrs.get('address','')

        user = User(
            username=username,
            email=email,
            name=name,
            phone_number = phone_number_str
        )

        if not (len(username)>5 and len(username)<=30 and username.isalnum()):
            raise serializers.ValidationError(
                'The username should only contain alphanumeric character and must be between 6 and 30 chars long'
            )

        if not name.replace(" ", "").isalpha():
            raise serializers.ValidationError('Please enter a valid name,Name should contain only alphabets')
            
        #email validation
        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            raise serializers.ValidationError('Email is not valid')

        #phone number validation
        try:
            phone_num = phonenumbers.parse(phone_number_str)
            if not phonenumbers.is_possible_number(phone_num):
                raise serializers.ValidationError("Phone number is not valid")
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError("Phone number is not valid")

        #dob validation
        if dob:
            try:
                date_of_birth = datetime.datetime.strptime(str(dob), "%Y-%m-%d")
            except:
                raise serializers.ValidationError("Incorrect data format, should be YYYY-MM-DD")

        #institute validation
        if institute:
            try:
                if not str(institute).replace(" ","").isalnum():
                    raise serializers.ValidationError("Enter valid institute name")
            except:
                raise serializers.ValidationError("Enter valid institute name")

        #address validation
        if address:
            try:
                validChar = "-,#.'/ "
                addr = str(address)
                for vchar in validChar:
                    addr = addr.replace(vchar,"")
                if not addr.isalnum():
                    raise serializers.ValidationError("Enter valid address format")

            except:
                raise serializers.ValidationError("Enter valid address format")

        #password validation
        pass_errors = dict() 
        try:
            # validate the password and catch the exception
            pass_validator.validate_password(password=password, user=user)

        # the exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            pass_errors['password'] = list(e.messages)

        if pass_errors:
            raise serializers.ValidationError(pass_errors)


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
        fields = ('username', 'name', 'email','phone_number','image','dob','institute','address')

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
        try:
            if not value.replace(" ", "").isalpha():
                raise serializers.ValidationError('Please enter a valid name,Name should contain only alphabets')
        except:
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

    def validate_dob(self,value):
        if value:
            try:
                date_of_birth = datetime.datetime.strptime(str(value), "%Y-%m-%d")
            except:
                raise serializers.ValidationError("Incorrect data format, should be YYYY-MM-DD")
        return value

    def validate_institute(self,value):
        if value:
            try:
                if not str(value).replace(" ","").isalnum():
                    raise serializers.ValidationError("Enter valid institute name")
            except:
                raise serializers.ValidationError("Enter valid institute name")
        return value

    def validate_address(self,value):
        if value:
            try:
                validChar = "-,#.'/ "
                addr = str(value)
                for vchar in validChar:
                    addr = addr.replace(vchar,"")
                if not addr.isalnum():
                    raise serializers.ValidationError("Enter valid address format")

            except:
                raise serializers.ValidationError("Enter valid address format")
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.id != instance.id:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})
        
        instance.name = validated_data.get('name',None) if validated_data.get('name',None) else user.name
        instance.phone_number = validated_data.get('phone_number',None) if validated_data.get('phone_number',None) else user.phone_number 
        instance.image = validated_data.get('image',None) if validated_data.get('image',None) else user.image
        instance.email = validated_data.get('email',None) if validated_data.get('email',None) else user.email
        instance.username = validated_data.get('username',None) if validated_data.get('username',None) else user.username
        instance.dob = validated_data.get('dob',None) if validated_data.get('dob',None) else user.dob
        instance.institute = validated_data.get('institute',None) if validated_data.get('institute',None) else user.institute
        instance.address =validated_data.get('address',None) if validated_data.get('address',None) else user.address

        if instance.email != user.email:
            instance.is_verified = False
            token = RefreshToken.for_user(user).access_token
            current_site = get_current_site(self.context['request']).domain
            relativeLink = reverse('email-verify')
            absurl = f'https://{current_site+relativeLink}?token={token}'
            email_body = "Hi "+user.username+",\n"+"Use below link to verify your email\n"+absurl
            data = {
                'to_email':user.email,
                'email_body':email_body,
                'email_subject':'Verify your email'
            }
            Util.send_email(data)
            # print(email_body)
            # print(instance.is_verified)

        instance.save()

        return instance