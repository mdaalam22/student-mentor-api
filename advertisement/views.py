from django.shortcuts import render
from rest_framework import permissions, serializers
from rest_framework.generics import CreateAPIView,ListAPIView
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.parsers import MultiPartParser,FormParser
from .serializers import AdsSerializer
from .models import Advertisement

# Create your views here.


class AdsCreateView(CreateAPIView):
    queryset = Advertisement.adsobjects.all()
    permission_classes = [IsAdminUser]
    parser_classes = (MultiPartParser,FormParser)
    serializer_class = AdsSerializer

class AdsListView(ListAPIView):
    queryset = Advertisement.adsobjects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = AdsSerializer

