from django.contrib.auth import tokens
from django.shortcuts import render
from rest_framework import generics, renderers, serializers, status,views
from rest_framework import permissions
from .serializers import (
    RegisterSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    RequestPasswordResetEmailSerializer,
    setNewPasswordSerializer,
    LogoutSerializer,
    ChangePasswordSerializer,
    UpdateUserSerializer,
    UserInfoSerializer,
    SendEmailVerifyLinkSerializer
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .renderers import UserRenderer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponsePermanentRedirect
import os
import environ
from django.conf import settings
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.views import APIView
from django.core.exceptions import ValidationError


env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'))


# Create your views here.

class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [env('APP_SCHEME'), 'http', 'https']
    

# class RegisterView(generics.GenericAPIView):
#     serializer_class = RegisterSerializer
#     renderer_classes = (UserRenderer,)

#     def post(self,request):
#         user = request.data
#         serializer = self.serializer_class(data=user)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         user_data = serializer.data
#         user = User.objects.get(email=user_data['email'])

#         token = RefreshToken.for_user(user).access_token
#         current_site = get_current_site(request).domain
#         relativeLink = reverse('email-verify')
#         absurl = f'http://{current_site+relativeLink}?token={token}'
#         email_body = "Hi "+user.username+",\n"+"Use below link to verify your email\n"+absurl
#         data = {
#             'to_email':user.email,
#             'email_body':email_body,
#             'email_subject':'Verify your email'
#         }
#         Util.send_email(data)

#         return Response(user_data,status=status.HTTP_201_CREATED)

class UserInfoView(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserInfoSerializer
    renderer_classes = (UserRenderer,)
    pagination_class  = None
  

    def get_queryset(self):
        queryset = User.objects.all()
        queryset = queryset.filter(username=self.request.user.username)
        if not queryset:
            raise ValidationError("user not found")

        return queryset

class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    parser_classes = [MultiPartParser,FormParser]


    def post(self,request,format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
        

            user_data = serializer.data
            user = User.objects.get(email=user_data['email'])

            token = RefreshToken.for_user(user).access_token
            current_site = get_current_site(request).domain
            relativeLink = reverse('email-verify')
            absurl = f'https://{current_site+relativeLink}?token={token}'
            email_body = "Hi "+user.username+",\n"+"Use below link to verify your email\n"+absurl
            data = {
                'to_email':user.email,
                'email_body':email_body,
                'email_subject':'Verify your email'
            }
            Util.send_email(data)

            return Response(user_data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter('token',in_=openapi.IN_QUERY,description="Description",type=openapi.TYPE_STRING)
    
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self,request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()

            return Response({'success':'Email successfully verified'},status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error':'Activation link expired'},status=status.HTTP_400_BAD_REQUEST)

        except jwt.exceptions.DecodeError as decodeerr:
            return Response({'error':'Invalid token'},status=status.HTTP_400_BAD_REQUEST)


class SendEmailVerifyLink(generics.GenericAPIView):
    serializer_class = SendEmailVerifyLinkSerializer
    
    def post(self,request):
       
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        email = request.data['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.is_verified:
                return Response({'error':'Your email is already verified'},status=status.HTTP_302_FOUND)
            token = RefreshToken.for_user(user).access_token
            current_site = get_current_site(request).domain
            relativeLink = reverse('email-verify')
            absurl = f'https://{current_site+relativeLink}?token={token}'
            email_body = "Hi "+user.username+",\n"+"Use below link to verify your email\n"+absurl
            data = {
                'to_email':user.email,
                'email_body':email_body,
                'email_subject':'Verify your email'
            }
            Util.send_email(data)
            return Response({'success':'We have sent you a link to verify your email'},status=status.HTTP_200_OK)
        else:
            return Response({'error':'User with this email does not exist'},status=status.HTTP_404_NOT_FOUND)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = RequestPasswordResetEmailSerializer
    def post(self,request):
       
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        email = request.data['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            redirect_url = request.data.get('redirect_url','')
            current_site = get_current_site(request=request).domain
            relativeLink = reverse('password-reset-confirm',
                kwargs={'uidb64':uidb64,'token':token})
            absurl = f'https://{current_site+relativeLink}'
            email_body = "Hello "+user.username+",\n Use below link to reset your password\n"+absurl+"?redirect_url="+redirect_url
            data = {
                'to_email':user.email,
                'email_body':email_body,
                'email_subject':'Reset your password'
            }
            Util.send_email(data)
            return Response({'success':'We have sent you a link to reset your password'},status=status.HTTP_200_OK)
        else:
            return Response({'error':'User with this email does not exist'},status=status.HTTP_404_NOT_FOUND)

class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = setNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url','')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url+'?token_valid=False')
                else:
                    return CustomRedirect(env('FRONTEND_URL', '')+'?token_valid=False')

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(redirect_url+'?token_valid=True&message=Credentials Valid&uidb64='+uidb64+'&token='+token)
            else:
                return CustomRedirect(env('FRONTEND_URL', '')+'?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user,token):
                    return CustomRedirect(redirect_url+'?token_valid=False')
                    
            except UnboundLocalError as e:
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)



class setNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = setNewPasswordSerializer
    def patch(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success':True,'message':'Password Reset Successfully'},status=status.HTTP_200_OK)



class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success':True,'message':'Logout Successfully'},status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer


class UpdateProfileView(generics.UpdateAPIView):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,FormParser)
    serializer_class = UpdateUserSerializer

# class UpdateProfileView(APIView):
#     queryset = User.objects.all()
#     parser_classes = (MultiPartParser,FormParser)
#     # permission_classes = [IsAuthenticated]

#     def put(self,request,format=None,*args,**kwargs):
#         qs = self.get_queryset()
#         serializer = UpdateUserSerializer(qs,data=request.data,context={'request': request})
#         if serializer.is_valid():
#             serializer.save()

#             return Response({'success':True,'message':'Profile Updated Successfully'},status=status.HTTP_200_OK)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)    