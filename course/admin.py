from django.contrib import admin
from django.db import models
from django.db.models import fields
from .models import Course,CourseContent,Question,Enrolled,PaymentDetail
from .forms import QuestionForm,CourseForm
# Register your models here.



# class QuestionAdmin(admin.StackedInline):
#     model = Question

class QuestionFilter(admin.SimpleListFilter):
    title = 'chapter'
    parameter_name = 'chapter_title'


    def lookups(self, request, model_admin):
        if 'course__course_name' in request.GET:
            course_name = request.GET['course__course_name']
            chapters = set([c.chapter for c in model_admin.model.objects.all().filter(course__course_name=course_name)])
        else:
            chapters = set([c.chapter for c in model_admin.model.objects.all()])
        return [(ch.id, ch.chapter_title) for ch in chapters]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(chapter__id__exact=self.value())
    


class ChapterAdmin(admin.TabularInline):
    model = CourseContent


class CourseAdmin(admin.ModelAdmin):
    form = CourseForm
    search_fields = ['course_name']
    readonly_fields = ('slug',)
    inlines = [ChapterAdmin]

class CourseContentAdmin(admin.ModelAdmin):
    form = QuestionForm
    # list_filter = ('course__course_name','chapter__chapter_title')
    list_filter = ('course__course_name',QuestionFilter,)

    class Media:
        js = (
            'js/chained.js',
        )
    

    # def has_add_permission(self, request, obj=None):
    #     return request.user.is_superuser or (obj and obj.id == request.user.id)



admin.site.register(Course,CourseAdmin)
admin.site.register(Question,CourseContentAdmin)


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