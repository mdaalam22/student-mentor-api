from django.core.exceptions import ValidationError
from django.db.models import fields
from rest_framework import serializers, status

from .models import Course,CourseContent, Enrolled,Question,PaymentDetail


class CourseSerializerView(serializers.ModelSerializer):
    slug = serializers.SlugField(max_length=255,read_only=True)
    status = serializers.CharField(max_length=50,write_only=True)

    class Meta:
        model = Course
        fields = ('course_name','image','grade','slug','description','original_fee','discount','is_premium','status')


# class CourseContentSerializerView(serializers.ModelSerializer):
#     course_contents = serializers.StringRelatedField(many=True)
#     questions = serializers.StringRelatedField(many=True)

#     class Meta:
#         model = Course
#         fields = ['course_name','grade','description','course_contents','questions']

class SearchViewSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField(source='course.id')
    course_name = serializers.CharField(source='course.course_name')
    course_slug = serializers.SlugField(source='course.slug')
    chapter_id = serializers.IntegerField(source='chapter.id')
    chapter_title = serializers.CharField(source='chapter.chapter_title')
    ques_id = serializers.IntegerField(source='id')
    class Meta:
        model = Question
        fields = ['course_id','course_name','course_slug','chapter_id','chapter_title','ques_id','question']
    
    def to_representation(self, data):
        data = super(SearchViewSerializer, self).to_representation(data)
        query = self.context.get('request').query_params.get('search')
        if not Course.objects.filter(id=data['course_id'],course_name__icontains=query):
            data['course_name'] = None
            data['course_slug'] = None
        if not CourseContent.objects.filter(id=data['chapter_id'],chapter_title__icontains=query):
            data['chapter_title'] = None
        
        if not Question.objects.filter(id=data['ques_id'],question__icontains=query):
            data['question'] = None
        
        return data


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id','question','answer','can_view','course','chapter']

    def to_representation(self, data):
        data = super(QuestionSerializer, self).to_representation(data)
        try:
            is_course = Course.courseobjects.get(id=data['course'])
            enrolled = Enrolled.objects.filter(user=self.context['request'].user,course=is_course).first()
            if enrolled:
                if is_course.is_premium_course():
                    if enrolled.paid:
                        data['can_view'] = True
                    elif not data['can_view']:
                        data['answer'] = 'premium'
                else:
                    data['can_view'] = True
            else:
                data['can_view'] = False
                data['answer'] = 'not_enrolled'
        except:
            raise serializers.ValidationError("Something went wrong")
        return data

class CourseContentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = CourseContent
        fields = '__all__'

    

class CourseSerializer(serializers.ModelSerializer):
    # course_name = serializers.CharField(max_length=255,required=False)
    # grade = serializers.CharField(max_length=50,required=False)
    # description = serializers.CharField(max_length=555,required=False)
    chapters = CourseContentSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class CourseEnrolledSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.course_name')
    image = serializers.ImageField(source='course.image')
    grade = serializers.CharField(source='course.grade')
    slug = serializers.CharField(source='course.slug')
    description = serializers.CharField(source='course.description')

    class Meta:
        model = Enrolled
        fields = ['course_name','image','grade','slug','description','enrolled_at','paid']


class StudentEnrolledSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.course_name',read_only=True)
    slug = serializers.CharField(source='course.slug',write_only=True)
    class Meta:
        model = Enrolled
        fields = ['course_name','slug']

    def validate(self, attrs):
        user = self.context['request'].user
        slug = self.context['slug']
        
        if slug:
            try:
                course = Course.courseobjects.get(slug=slug)
            except:
                raise serializers.ValidationError("Course not found")
        
            if not course:
                raise serializers.ValidationError("Course Not Found")

            if Enrolled.objects.filter(user=user,course=course).exists():
                raise serializers.ValidationError("You are already enrolled to this course")
        
        else:
            raise serializers.ValidationError("Bad Request")

        return attrs


class ChapterViewSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField(source='course.id')
    course_name = serializers.CharField(source='course.course_name')
    is_premium = serializers.BooleanField(source='course.is_premium')
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = CourseContent
        fields = ['course_id','course_name','is_premium','id','chapter_title','questions']


class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDetail
        fields = '__all__'