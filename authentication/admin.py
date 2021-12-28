from django.contrib import admin
from .models import User
from  django.contrib.auth.models  import  Group
from rest_framework_simplejwt import token_blacklist


# Register your models here.

class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('username','email','is_verified','is_active','is_staff','is_superuser')
    search_fields = ['username']
    exclude = ('dob','institute','address')

    
    # def has_change_permission(self, request, obj=None):
    #     return request.user.is_superuser or (obj and obj.id == request.user.id)


admin.site.register(User,UserAdmin)

admin.site.unregister(Group)

class OutstandingTokenAdmin(token_blacklist.admin.OutstandingTokenAdmin):

    def has_delete_permission(self, *args, **kwargs):
        return True 

admin.site.unregister(token_blacklist.models.OutstandingToken)
admin.site.register(token_blacklist.models.OutstandingToken, OutstandingTokenAdmin)
