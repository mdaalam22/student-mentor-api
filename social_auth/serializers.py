from rest_framework import serializers
import google
from .google import Google
import environ
import os
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .registers import register_social_user

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'))


class GoogleSocialAuthSerializer(serializers.Serializer):
    
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = Google.validate(auth_token)
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )

        if user_data['aud'] != env('GOOGLE_CLIENT_ID'):
            raise AuthenticationFailed('oops, who are you?')

        user_id = user_data['sub']
        email = user_data['email']
        name = user_data['name']
        image = user_data['picture']
        provider = 'google'

        return register_social_user(
            provider=provider, user_id=user_id, email=email, name=name,image=image)

        