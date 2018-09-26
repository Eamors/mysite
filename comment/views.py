from django.http import JsonResponse
from django.shortcuts import reverse
from django.core.mail import send_mail
from comment.forms import CommentForm
from .models import Comment
from django.conf import settings

def update_comment(request):
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    comment_form = CommentForm(request.POST,user=request.user)
    data = {}
    if comment_form.is_valid():
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']

        parents = comment_form.cleaned_data['parent']
        if not parents is None:
            comment.root = parents.root if not parents.root is None else parents
            comment.parent = parents
            comment.reply_to = parents.user
        comment.save()

        # 多线程发送邮件
        comment.send_mail()

        # 回复邮件通知
        # if comment.parent is None:
        #     subject = '有人评论你的博客'
        #     email = comment.content_object.get_email()
        # else:
        #     subject = '有人回复你的评论'
        #     email = comment.reply_to.email
        #
        # if email !='':
        #     text = comment.text + '\n' + comment.content_object.get_url()
        #     send_mail(
        #         subject,text,settings.EMAIL_HOST_USER,[email],fail_silently=False,
        #     )

            # 返回数据
        data['status'] = "SUCCESS"
        data['username'] = comment.user.get_nickname_or_username()
        # data['comment_time'] = comment.comment_time.strftime('%Y-%m-%d %H:%M:%S')
        data['comment_time'] = comment.comment_time.timestamp()
        data['text'] = comment.text
        if not parents is None:
            data['reply_to'] = comment.reply_to.get_nickname_or_username()
        else:
            data['reply_to'] = ''
        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if not comment.root is None else ''
        # return redirect(referer)
    else:
        # return render(request, 'error.html', {'message': comment_form.errors, 'redirect_to': referer})
        data['status'] = "ERROR"
        data['message'] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)
    '''
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    if not request.user.is_authenticated:
        return render(request,'error.html',{'message':'用户未登录','redirect_to':referer})
    text = request.POST.get('text','').strip()
    if text == '':
        return (request,'error.html',{'message':'评论不能为空','redirect_to':referer})

    try:
        content_type = request.POST.get('content_type','')
        object_id = request.POST.get('object_id','')
        model_class = ContentType.objects.get(model=content_type).model_class()
        model_obj = model_class.objects.get(pk = object_id)
    except Exception as e:
        return render(request,'error.html',{'message':'评论对象不存在','redirect_to':referer})
    comment = Comment()
    comment.user = request.user
    comment.text = text
    comment.content_object = model_obj
    comment.save()
    return redirect(referer)
    '''



