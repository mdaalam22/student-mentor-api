from django.db import models
from authentication.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from studentnote.utils import unique_slug_generator
from django_ckeditor_5.fields import CKEditor5Field


# Create your models here.



class Course(models.Model):

    class CourseObjects(models.Manager):
        def get_queryset(self):
            return super().get_queryset() .filter(status='published')

    options = (
        ('published','Published'),
        ('draft','Draft')
    )

    course_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length = 255, null = True, blank = True)
    grade = models.CharField(max_length=80)
    description = models.TextField()
    original_fee = models.FloatField()
    discount = models.FloatField()
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=30,choices=options,default='published')

    objects = models.Manager()
    courseobjects = CourseObjects()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.course_name


@receiver(pre_save, sender=Course)
def pre_save_receiver(sender, instance, *args, **kwargs):
   if not instance.slug:
       instance.slug = unique_slug_generator(instance)


class CourseContent(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='chapters')
    chapter_title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.chapter_title


class Question(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='course_ques')
    chapter = models.ForeignKey(CourseContent,on_delete=models.CASCADE,related_name='questions')
    question = CKEditor5Field(config_name="editor")
    answer = CKEditor5Field(config_name="editor")
    edited_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Enrolled(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='student_course')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = 'enrolled'