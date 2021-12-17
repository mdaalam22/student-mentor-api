from django.contrib import admin
from django.db import models
from django.db.models import fields
from .models import Course,CourseContent,Question,Enrolled
from pagedown.widgets import AdminPagedownWidget
# Register your models here.



class QuestionAdmin(admin.StackedInline):
    model = Question
    


class ChapterAdmin(admin.TabularInline):
    model = CourseContent


class CourseAdmin(admin.ModelAdmin):
    model = Course
    inlines = [ChapterAdmin]

class CourseContentAdmin(admin.ModelAdmin):
    model = CourseContent
    inlines = [QuestionAdmin]

    list_filter = ('course',)
    

    # def has_add_permission(self, request, obj=None):
    #     return request.user.is_superuser or (obj and obj.id == request.user.id)



admin.site.register(Course,CourseAdmin)
admin.site.register(CourseContent,CourseContentAdmin)


class EnrolledAdmin(admin.ModelAdmin):
    model = Enrolled
    display_field = ('user','course')

admin.site.register(Enrolled,EnrolledAdmin)
