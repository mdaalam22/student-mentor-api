from django.urls import path
from .views import (CourseCreateAPIView,
CourseListAPIView,
CourseUpdateAPIView,
CourseDetailView,
CourseDeleteAPIView,
CourseContentView,
CourseEnrolledView,
StudentEnrolledView,
NewCourseView,
PopularCourseView,
PaymentDetailView
)

app_name ='course'
urlpatterns = [
    path('all/',CourseListAPIView.as_view(),name='all_course'),
    path('detail/<slug:slug>/',CourseDetailView.as_view(),name='course_detail'),
    path('create/',CourseCreateAPIView.as_view(),name='create_course'),
    path('update/<slug:slug>/',CourseUpdateAPIView.as_view(),name='update_course'),
    path('delete/<slug:slug>/',CourseDeleteAPIView.as_view(),name='delete_course'),
    path('content/<slug:slug>/',CourseContentView.as_view({'get': 'retrieve'}),name='course_content'),
    path('mycourse/',CourseEnrolledView.as_view(),name='enrolled_course'),
    path('enroll/',StudentEnrolledView.as_view(),name='enroll'),
    path('new-course/',NewCourseView.as_view(),name='new-course'),
    path('popular-course/',PopularCourseView.as_view(),name='popular-course'),
    path('payment-detail/',PaymentDetailView.as_view(),name='payment-detail'),
]
