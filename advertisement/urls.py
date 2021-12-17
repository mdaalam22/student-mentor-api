from django.urls import path
from .views import AdsListView,AdsCreateView

urlpatterns = [
    path('create/',AdsCreateView.as_view(),name='create-ad'),
    path('list/',AdsListView.as_view(),name='list-ads'),
]
