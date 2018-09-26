from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from user.forms import LoginForm
from read_count.utils import *

each_blog_num = settings.EACH_BLOG_NUM


def same_code(request,blogs_all_list):
    paginator = Paginator(blogs_all_list, each_blog_num)  # 每十条为一页
    page_num = request.GET.get('page', 1)  # 获取页码参数
    page_of_blogs = paginator.get_page(page_num)  # 获取当前页

    current_page_num = page_of_blogs.number
    # print(current_page_num)
    # page_range = [current_page_num - 2,current_page_num-1,current_page_num,current_page_num+1,current_page_num+2]
    # 获取当前页码前后各两页的页码范围
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) \
                 + list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))
    # 加上省略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)
    # page_of_blogs.object_list获取当前页的所有文章
    blog_with_dict = {}
    # print(Blog.objects.dates('create_time', 'month', order="DESC"))<QuerySet [datetime.date(2018, 9, 1)]>

    for blog_date in Blog.objects.dates('create_time', 'month', order="DESC"):
        # print(blog_date)2018-09-01
        blog_count = Blog.objects.filter(create_time__year=blog_date.year,
                                         create_time__month=blog_date.month).count()
        print(blog_count)
        blog_with_dict[blog_date] = blog_count
    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    context['page_range'] = page_range
    context['blog_date'] = blog_with_dict
    return context

def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = same_code(request,blogs_all_list)
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request,blog_pk):
    context = {}
    context['blog'] = get_object_or_404(Blog,pk = blog_pk)
    blog = get_object_or_404(Blog,pk = blog_pk)
    read_cookie_key = read_count_once_read(request,blog)
    # blog_content_type = ContentType.objects.get_for_model(blog)
    # comments = Comment.objects.filter(content_type=blog_content_type,object_id=blog_pk,parent=None)
    '''
    if not request.COOKIES.get("read_{}_ok".format(blog.pk))
        if ReadNum.objects.filter(blog = blog).count():
            readnum = ReadNum.objects.get(blog = blog)
        else:
            readnum = ReadNum(blog = blog)
        blog.read_num += 1
        blog.save()
    '''
    context['previous'] = Blog.objects.filter(create_time__gt=blog.create_time).last()
    context['next_blog'] = Blog.objects.filter(create_time__lt=blog.create_time).first()
    context['blog'] = blog
    context['login_form'] = LoginForm()
    # context['comment'] = comments.order_by('-comment_time')
    # data = {}
    # context['content_type'] = blog_content_type
    # data['object_id'] = blog_pk
    # context['comment_form'] = CommentForm(initial={'content_type':blog_content_type.model,'object_id':blog_pk,'reply_comment_id':0})
    # context['user'] = request.user
    response =  render(request, 'blog/blog_detail.html', context)
    response.set_cookie(read_cookie_key,'true')
    # response.set_cookie("read_{}_ok".format(blog.pk),'true')
    return response

def blog_with_type(request,blogs_type_pk):
    blog_type = BlogType.objects.get(pk = blogs_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = same_code(request,blogs_all_list)
    context['blog_type'] = blog_type
    context['blog_type_count'] = Blog.objects.filter(blog_type=blog_type).count()
    return render(request, 'blog/blog_with_type.html', context)

def blogs_with_date(request,year,month):
    context = {}
    print(year,month)
    # 根据传过来的时间，获取时间段内的所有博客
    blogs_all_list = Blog.objects.filter(create_time__year=year,create_time__month=month)
    context = same_code(request,blogs_all_list)
    context['blog_with_date'] = '{}年{}月'.format(year,month)
    # context['blog_with_date_count'] = blogs_all_list.count()
    return render(request,'blog/blog_with_date.html',context)

# def page(request):
#     blogs_all_list = Blog.objects.all()
#     context = same_code(request,blogs_all_list)
#     return render(request,'blog/blog_list.html',context)