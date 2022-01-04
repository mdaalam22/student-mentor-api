from django.contrib import admin
from django.db import models
from django.db.models import fields
from .models import Course,CourseContent,Question,Enrolled,PaymentDetail
# Register your models here.



class QuestionAdmin(admin.StackedInline):
    model = Question
    


class ChapterAdmin(admin.TabularInline):
    model = CourseContent


class CourseAdmin(admin.ModelAdmin):
    model = Course
    search_fields = ['course_name']
    readonly_fields = ('slug',)
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
    list_filter = ('course__course_name','paid')
    search_fields = ('user__username','course__course_name')

    

admin.site.register(Enrolled,EnrolledAdmin)


class PaymentDetailAdmin(admin.ModelAdmin):
    model = PaymentDetail
    list_display = ('image','uploaded_at')
    readonly_fields = ('uploaded_at',)

admin.site.register(PaymentDetail,PaymentDetailAdmin)