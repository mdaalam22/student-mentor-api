from django.core.exceptions import ValidationError
from rest_framework import serializers, status
from .models import Course,CourseContent, Enrolled,Question


class CourseSerializerView(serializers.ModelSerializer):
    slug = serializers.SlugField(max_length=255,read_only=True)
    status = serializers.CharField(max_length=50,write_only=True)

    class Meta:
        model = Course
        fields = ('course_name','grade','slug','description','original_fee','discount','status')


# class CourseContentSerializerView(serializers.ModelSerializer):
#     course_contents = serializers.StringRelatedField(many=True)
#     questions = serializers.StringRelatedField(many=True)

#     class Meta:
#         model = Course
#         fields = ['course_name','grade','description','course_contents','questions']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

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
    grade = serializers.CharField(source='course.grade')
    description = serializers.CharField(source='course.description')

    class Meta:
        model = Enrolled
        fields = ['course_name','grade','description','enrolled_at']


class StudentEnrolledSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.course_name',read_only=True)
    slug = serializers.CharField(source='course.course_name',write_only=True)
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