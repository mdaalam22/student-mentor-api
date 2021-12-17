from django.contrib import admin
from .models import Advertisement

# Register your models here.
@admin.register(Advertisement)
class AdsAdmin(admin.ModelAdmin):
    list_display = ('title','priority','active','created_at')
    list_filter = ('priority','active','created_at')
