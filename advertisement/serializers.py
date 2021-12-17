from django.db.models import fields
from rest_framework import serializers
from .models import Advertisement


class AdsSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    active = serializers.BooleanField(write_only=True)
    class Meta:
        model = Advertisement
        fields = ['title','image','priority','active','created_at']