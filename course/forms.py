from django import forms
from django.db.models import fields
from .models import Course,CourseContent,Question
from authentication.models import User
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)

        # when there is instance key, select the default value
        # Course always loaded for initial data, because Course is on the first level 
        try:
            self.initial['course'] = kwargs['instance'].course.id
        except:
            pass
        course_list = [('', '---------')] + [(i.id, i.course_name) for i in Course.courseobjects.all()]

        
        try:
            self.initial['chapter'] = kwargs['instance'].chapter.id
            chapter_init_form = [(i.id, i.chapter_title) for i in CourseContent.objects.filter(
                course=kwargs['instance'].course
            )]
        except:
            chapter_init_form = [('', '---------')]

        # Override the form, add onchange attribute to call the ajax function
        self.fields['course'].widget = forms.Select(
            attrs={
                'id': 'id_course',
                'onchange': 'getChapter(this.value)',
                'style': 'width:200px'
            },
            choices=course_list,
        )

        #override from to only show superuser
        self.fields['edited_by'].widget = forms.Select(
            
            choices=[('', '---------')] + [(i.id, i.username) for i in User.objects.filter(is_superuser=True)],
        )
       
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_name','image','grade','slug','description','original_fee','discount','is_premium','author','status']
    
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        self.fields['author'].widget = forms.Select(
        
            choices=[('', '---------')] + [(i.id, i.username) for i in User.objects.filter(is_superuser=True)],
        )