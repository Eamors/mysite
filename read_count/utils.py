from read_count.models import *
from blog.models import *
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import datetime
from django.db.models import Sum


def read_count_once_read(request,obj):
    ct = ContentType.objects.get_for_model(Blog)
    key = "{}_{}_read".format(ct.model,obj.pk)
    if not request.COOKIES.get(key):
        # 获取Blog模型

        # 总阅读数＋１
        # if ReadNum.objects.filter(content_type=ct,object_id=obj.pk).count():
        #     readnum = ReadNum.objects.get(content_type=ct,object_id=obj.pk)
        # else:
        #     # 如果没有，则进行实例化对象
        #     readnum = ReadNum(content_type=ct,object_id=obj.pk)
        # print(readnum)

        readnum,created = ReadNum.objects.get_or_create(content_type=ct,object_id=obj.pk)
        readnum.read_num += 1
        readnum.save()

        # 当天阅读数＋１
        date = timezone.now().date()
        # if ReadDetail.objects.filter(content_type=ct,object_id=obj.pk,date=date).count():
        #     readDetail = ReadDetail.objects.filter(content_type=ct, object_id=obj.pk, date=date)
        # else:
        #     readDetail = ReadDetail(content_type=ct, object_id=obj.pk, date=date)
        readDetail,created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)
        readDetail.read_num += 1
        readDetail.save()
    return key

def get_seven_days_data(content_type):
    today = timezone.now().date()
    reads_num = []
    dates = []
    for i in range(7,0,-1):
        print(i)
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        read_detail = ReadDetail.objects.filter(content_type=content_type,date=date)
        # 此处的result返回的是一个字典{'read_num_sum': 7}
        result =  read_detail.aggregate(read_num_sum = Sum('read_num'))
        reads_num.append(result['read_num_sum'] or 0)
        print(date)
    return dates,reads_num


def get_today_hot_data(content_type):
    today = timezone.now().date()
    read_detail = ReadDetail.objects.filter(content_type=content_type,date=today).order_by('-read_num')
    return read_detail[:3]

def get_yesterday_hot_data(content_type):
    today = timezone.now().date()
    yesterday =  today - datetime.timedelta(days=1)
    read_detail = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by('-read_num')
    return read_detail[:3]

# def get_7_days_hot_blogs(content_type):
#     today = timezone.now().date()
#     date = today - datetime.timedelta(days=7)
#     read_detail = ReadDetail.objects.filter(content_type=content_type,date__lt=today,
#                                             date__gte=date)\
#                                             .values('content_type','object_id')\
#                                             .annotate(read_num_sum = Sum('read_num'))\
#                                             .order_by('read_num_sum')
#     return read_detail[:7]