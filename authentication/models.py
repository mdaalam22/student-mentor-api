from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,BaseUserManager,PermissionsMixin
)
from rest_framework_simplejwt.tokens import RefreshToken


# Create your models here.


def default_img():
    return f'profile_img/default.jpg'


def upload_img(instance,filename):
    return f'profile_img/{filename}'

class UserManager(BaseUserManager):

    def create_user(self,username,name,email,phone_number,image=None,dob=None,institute=None,address=None,password=None):
        if username is None:
            raise TypeError("User should have a username")
        if email is None:
            raise TypeError("User should have an email")
        
        if image is None:
            image = default_img()

        user = self.model(username=username,name=name,email=self.normalize_email(email),phone_number=phone_number,image=image,dob=dob,institute=institute,address=address)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self,username,name,email,phone_number,image,password=None):
        if password is None:
            raise TypeError("Password should not be none")

        user = self.create_user(username,name,email,phone_number,image,password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user

AUTH_PROVIDERS = {'google':'google','email':'email'}

class User(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(max_length=255,unique=True,db_index=True)
    name = models.CharField(max_length=60)
    email = models.EmailField(max_length=255,unique=True,db_index=True)
    phone_number = models.CharField(max_length=20)
    image = models.ImageField(upload_to=upload_img,default="profile_img/default.jpg")
    dob = models.DateField(null=True,blank=True)
    institute = models.CharField(max_length=255,null=True,blank=True)
    address = models.CharField(max_length=60,null=True,blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    auth_provider = models.CharField(max_length=255,null=False,blank=False,default=AUTH_PROVIDERS.get('email'))

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name','email','phone_number','image']

    objects = UserManager()

    def __str__(self):
        return self.username
    
    def __unicode__(self):
        return self.username

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }



