from django.db import models
from authentication.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from studentnote.utils import unique_slug_generator
from django_ckeditor_5.fields import CKEditor5Field
import lxml.html
from PIL import Image
from bs4 import BeautifulSoup
from django.conf import settings
import os

# Create your models here.

def upload_img(instance,filename):
    return f'course_img/{filename}'

def upload_payment_img(instance,filename):
    return f'payment_img/{filename}'


class Course(models.Model):

    class CourseObjects(models.Manager):
        def get_queryset(self):
            return super().get_queryset() .filter(status='published')

    options = (
        ('published','Published'),
        ('draft','Draft')
    )

    course_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=upload_img,default="course_img/default.jpg")
    slug = models.SlugField(max_length = 255, null = True, blank = True)
    grade = models.CharField(max_length=80)
    description = models.TextField()
    original_fee = models.FloatField(default=0)
    discount = models.FloatField(default=0)
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_premium = models.BooleanField(default=True)
    status = models.CharField(max_length=30,choices=options,default='published')

    objects = models.Manager()
    courseobjects = CourseObjects()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.course_name

    def __unicode__(self):
        return self.course_name

    def is_premium_course(self):
        return self.is_premium
    
    def save(self, *args, **kwargs):
       super(Course, self).save(*args, **kwargs)
       image = Image.open(self.image.path)
       image.save(self.image.path,quality=20,optimize=True)


@receiver(pre_save, sender=Course)
def pre_save_receiver(sender, instance, *args, **kwargs):
   if not instance.slug:
       instance.slug = unique_slug_generator(instance)


class CourseContent(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='chapters')
    chapter_title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.chapter_title

def findImageToCompress(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    try:
        for item in soup.find_all('img'):
            image_path=os.path.join(settings.MEDIA_ROOT,item['src'][7:])
            image = Image.open(image_path)
            image.save(image_path,quality=20,optimize=True)

    except:
        pass

class Question(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='course_ques')
    chapter = models.ForeignKey(CourseContent,on_delete=models.CASCADE,related_name='questions')
    question = CKEditor5Field(config_name="editor")
    answer = CKEditor5Field(config_name="editor")
    can_view = models.BooleanField(default=False)
    edited_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return lxml.html.fromstring(self.question).text_content() if self.question else ''

    def save(self, *args, **kwargs):
       super(Question, self).save(*args, **kwargs)
       findImageToCompress(self.question)
       findImageToCompress(self.answer)


class Enrolled(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='student_course')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = 'enrolled'

    def __str__(self) -> str:
        return f'{self.user.username} - {self.course.course_name}'


class PaymentDetail(models.Model):
    image = models.ImageField(upload_to=upload_payment_img,default="payment_img/default.jpg")
    uploaded_at = models.DateTimeField(auto_now_add=True)
