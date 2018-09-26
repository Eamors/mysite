from django.shortcuts import render
from .models import LikeCount,LikeRecord
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist

def error_response(code,message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)

def success_response(liked_num):
    data = {}
    data['status'] = 'SUCCESS'
    data['like_num'] = liked_num
    return JsonResponse(data)

def like_change(request):
    user = request.user
    if not user.is_authenticated:
        return error_response(400,'你还没有登陆呢')

    content_type = request.GET.get('content_type')
    object_id = int(request.GET.get('object_id'))
    try:
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_obj = model_class.objects.get(pk = object_id)
    except ObjectDoesNotExist:
        return error_response(401,'对象不存在')

    if request.GET.get('is_like') == 'true':
        # 要点赞
        like_record,create = LikeRecord.objects.get_or_create(content_type = content_type,object_id=object_id,user = user)

        if create:
            # 没有点赞过，进行点赞
            like_count,create = LikeCount.objects.get_or_create(content_type=content_type,object_id=object_id)
            like_count.like_num += 1
            like_count.save()
            return success_response(like_count.like_num)
        else:
            # 已经点赞，无需再次点赞
            return error_response(402,'你已经点赞过')
    else:
        # 取消点赞
        if LikeRecord.objects.filter(content_type=content_type,object_id=object_id,user=user).exists():
            like_record = LikeRecord.objects.get(content_type=content_type,object_id=object_id,user=user)
            like_record.delete()
            like_count,create = LikeCount.objects.get_or_create(content_type=content_type,object_id=object_id,)
            if not create:
                # 有点赞过，取消点赞
                like_count.like_num -= 1
                like_count.save()
                return success_response(like_count.like_num)
            else:
                return error_response(404, '数据有误')
        else:
            return error_response(403, '你还没有点赞嫩')
