from django.core.cache import cache
from django.shortcuts import render

from blog.models import *
from read_count.utils import *


def get_7_days_hot():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects\
                .filter(read_details__date__lt = today,read_details__date__gte = date)\
                .values('id','title')\
                .annotate(read_num_sum = Sum('read_details__read_num'))\
                .order_by('-read_num_sum')
    return blogs[:3]

def home(request):
    context = {}
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates,read_num = get_seven_days_data(blog_content_type)
    get_7_day_hot = cache.get('get_7_day_hot')
    #设置缓存
    if get_7_day_hot is None:
        get_7_day_hot = get_7_days_hot()
        # 三个参数　缓存的键名，键值，有效期
        cache.set('get_7_day_hot',get_7_day_hot,3600)
        print('calc')
    else:
        print('use')

    hot_blogs = cache.get('get_yesterday_hot_data')
    context['read_num'] = read_num
    context['dates'] = dates
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['get_yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['get_7_day_hot'] = get_7_day_hot
    return render(request,'home.html',context)




