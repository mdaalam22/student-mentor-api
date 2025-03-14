from django.contrib.auth import authenticate
from authentication.models import User
import os
import environ
import random
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from rest_framework.response import Response
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'))

def generate_username(name):

    username = "".join(name.split(' ')).lower()
    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + str(random.randint(0, 1000))
        return generate_username(random_username)


def register_social_user(provider, user_id, email,name,image):
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():

        if provider == filtered_user_by_email[0].auth_provider:
            user = User.objects.get(email=email)
            print(user.username)
            registered_user = authenticate(
                username=user.username, password=env('SOCIAL_SECRET'))
            if registered_user:
                return {
                    'username': registered_user.username,
                    'email': registered_user.email,
                    'tokens': registered_user.tokens()}
            else:
                raise AuthenticationFailed("Failed to authenticate")

        else:
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

    else:
        user = {
            'username': generate_username(name), 'email': email,
            'password': env('SOCIAL_SECRET'),
            'name':name,
            'image':image,
            'phone_number':''}
        user = User.objects.create_user(**user)
        user.is_verified = True
        user.auth_provider = provider
        user.save()

        new_user = authenticate(
            username=user.username, password=env('SOCIAL_SECRET'))
       
        if new_user:
            return {
                'email': new_user.email,
                'username': new_user.username,
                'tokens': new_user.tokens()
            }
        raise AuthenticationFailed("Failed to authenticate")