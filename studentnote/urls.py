from django.contrib import admin
from django.urls import path,include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import url
from django.views.static import serve

schema_view = get_schema_view(
   openapi.Info(
      title="Student Mentor API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.example.com/policies/terms/",
      contact=openapi.Contact(email="contact@example.local"),
      license=openapi.License(name="Test License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    path('admin/', admin.site.urls),
    path('auth/',include('authentication.urls')),
    path('social_auth/',include(('social_auth.urls','social_auth'),namespace="social_auth")),
    path('course/',include('course.urls')),
    path('ads/',include('advertisement.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


admin.site.site_header  =  "Student Mentor admin"  
admin.site.site_title  =  "Student Mentor admin site"
admin.site.index_title  =  "Student Mentor Admin"