from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.blog_list,name="blog_list"),
    path('<int:blog_pk>',views.blog_detail,name = 'blog_detail'),
    path('blog/<int:blogs_type_pk>',views.blog_with_type,name="blog_with_type"),
    path('date/<int:year>/<int:month>',views.blogs_with_date,name="blogs_with_date"),
    # path('page/',views.page,name="page")

]