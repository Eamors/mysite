from django.contrib import admin
from .models import BlogType,Blog
# from .models import BlogType,Blog,ReadNum


@admin.register(BlogType)
class BlogType(admin.ModelAdmin):
    list_display = ['id','type_name']


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['id','title','blog_type','author','readnums','create_time','last_update_time']

    '''
        list_display = ['title', 'blog_type', 'author', 'read_num', 'create_time', 'last_update_time']
    '''

# Register your models here.
'''
@admin.register(ReadNum)
class ReadNumAdmin(admin.ModelAdmin):
    list_display = ['read_num','blog']
'''