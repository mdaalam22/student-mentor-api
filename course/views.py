from django.shortcuts import render
from rest_framework import generics,status,viewsets
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser

from authentication import serializers
from course.admin import PaymentDetailAdmin
from .models import Course, CourseContent, Enrolled,PaymentDetail, Question
from .serializers import (
CourseSerializerView,
CourseSerializer,
CourseContentSerializer,
CourseEnrolledSerializer,
QuestionSerializer,
StudentEnrolledSerializer,
PaymentDetailSerializer,
ChapterViewSerializer,
SearchViewSerializer
)
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter

from django.db.models import Count

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from rest_framework import filters
# Create your views here.

class MultipleFieldLookupMixin(object):
   def get_object(self):

       queryset = self.get_queryset()
       queryset = self.filter_queryset(queryset)
       filter = {}
       for field in self.lookup_fields:
           if self.kwargs.get(field, None):
               filter[field] = self.kwargs[field]
               obj = get_object_or_404(queryset, ** filter) # Lookup the object
               self.check_object_permissions(self.request, obj)
       return obj


# == view to load chapter list of the selected course dynamically ==
@login_required
def chapter_list(request,course_id):
    chapters = CourseContent.objects.filter(course=course_id)
    return JsonResponse({'data': [{'id': chap.id, 'chapter_title': chap.chapter_title} for chap in chapters]})
#================end view==============

class CourseCreateAPIView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = CourseSerializerView(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(status=status.HTTP_201_CREATED)

class CourseListAPIView(generics.ListAPIView):
    queryset = Course.courseobjects.all()
    serializer_class = CourseSerializerView
    permission_classes = (IsAuthenticated,)

class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializerView
    permission_classes = (IsAuthenticated,)
    lookup_field = "slug"

    def get_object(self, queryset=None): 
        slug = self.kwargs.get('slug')
        obj = Course.courseobjects.get(slug=slug)
        return obj

class CourseUpdateAPIView(generics.UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializerView
    permission_classes = (IsAdminUser,)

    lookup_field = "slug"

    def get_object(self, queryset=None): 
        slug = self.kwargs.get('slug')
        obj = Course.courseobjects.get(slug=slug)
        return obj

class CourseDeleteAPIView(generics.DestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializerView
    permission_classes = (IsAdminUser,)

    lookup_field = "slug"

    def get_object(self, queryset=None): 
        slug = self.kwargs.get('slug')
        obj = Course.courseobjects.get(slug=slug)
        return obj

class CourseContentView(viewsets.ModelViewSet):
    queryset = Course.courseobjects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated,)
    
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Course.courseobjects.all()
        slug = self.kwargs['slug']
        if not slug:
            raise ValidationError("Bad request")
        try:
            queryset = Course.courseobjects.get(slug=slug)
            if not queryset:
                raise ValidationError("Course not found")
        except:
            raise ValidationError("Course not found")

        
        is_enrolled = Enrolled.objects.filter(user=self.request.user,course=queryset).exists()
        if not is_enrolled:
            raise ValidationError("You are not enrolled to this course")

        queryset = Course.courseobjects.filter(slug=slug)
        
    

        return queryset

#list all the course enrolled by a student
class CourseEnrolledView(generics.ListAPIView):
    queryset = Enrolled.objects.all()
    serializer_class = CourseEnrolledSerializer
    permission_classes = (IsAuthenticated,)


    def get_queryset(self):
        queryset = Enrolled.objects.all()
        queryset = queryset.filter(user=self.request.user).all()
        if not queryset:
            raise ValidationError("You are not enrolled to any courses")

        return queryset


class StudentEnrolledView(generics.GenericAPIView):
    queryset = Course.courseobjects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = StudentEnrolledSerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data,context={'request':request,'slug':request.data['slug']})
        serializer.is_valid(raise_exception=True)
        course = Course.objects.get(slug=request.data['slug'])
        serializer.save(user=request.user,course=course)
        return Response({'success':True,'message':'You are successfully enrolled to this course'},status=status.HTTP_201_CREATED)


class NewCourseView(generics.ListAPIView):
    queryset = Course.courseobjects.order_by('-created_at')[:5]
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializerView

class PopularCourseView(generics.ListAPIView):
    queryset = Course.courseobjects.annotate(enroll_count = Count('student_course')).order_by('-enroll_count')[:5]
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializerView


class QuestionView(MultipleFieldLookupMixin,generics.RetrieveAPIView):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = QuestionSerializer
    lookup_fields = ['course_id','chapter_id','id']

    def get_queryset(self):
        user = self.request.user
        course_id = self.kwargs['course_id']
        chap_id = self.kwargs['chap_id']
        ques_id = self.kwargs['ques_id']
        if course_id and chap_id and ques_id:
            try:
                queryset = Question.objects.filter(id=ques_id,chapter_id=chap_id,course_id=course_id)
            except:
                return Response({'Chapter not found'},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'Enter valid course_id,chapter_id and ques_id'
            },status=status.HTTP_400_BAD_REQUEST)
        
        return queryset

class ChapterView(generics.ListAPIView):
    queryset = CourseContent.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChapterViewSerializer

    def get_queryset(self):
        user = self.request.user
        course_id = self.kwargs['course_id']
        chap_id = self.kwargs['chap_id']
        if course_id and chap_id:
            try:
                queryset = CourseContent.objects.filter(id=chap_id,course_id=course_id)
            except:
                return Response({'Chapter not found'},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'Enter valid course_id and chapter_id'
            },status=status.HTTP_400_BAD_REQUEST)


        return queryset



    

class PaymentDetailView(generics.ListAPIView):
    queryset = PaymentDetail.objects.order_by('-uploaded_at')[:1]
    serializer_class = PaymentDetailSerializer



class SearchView(generics.ListAPIView):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SearchViewSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['course__course_name','chapter__chapter_title','question']