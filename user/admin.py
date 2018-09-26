from .models import Profile
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseAdmin
from django.contrib.auth.models import User

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class UserAdmin(BaseAdmin):
    inlines = (ProfileInline,)
    list_display = ('username','nickname','email','is_staff','is_active','is_superuser')

    def nickname(self,obj):
        return obj.profile.nickname
    # 将昵称以中文注册进ａｄｍｉｎ
    nickname.short_description = "昵称"

admin.site.unregister(User)
admin.site.register(User,UserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','nickname')