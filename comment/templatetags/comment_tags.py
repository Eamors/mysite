from django import template
from django.contrib.contenttypes.models import ContentType

from comment.forms import CommentForm
from ..models import Comment

register = template.Library()

@register.simple_tag
def get_comment_count(obj):
    blog_content_type = ContentType.objects.get_for_model(obj)
    return Comment.objects.filter(content_type=blog_content_type, object_id=obj.pk).count()

@register.simple_tag
def get_comment_form(obj):
    blog_content_type = ContentType.objects.get_for_model(obj)
    form = CommentForm(initial={'content_type': blog_content_type.model,
                         'object_id': obj.pk,
                         'reply_comment_id': 0})
    return form



#获取评论的列表
@register.simple_tag
def get_comment_list(obj):
    blog_content_type = ContentType.objects.get_for_model(obj)
    comment = Comment.objects.filter(content_type=blog_content_type, object_id=obj.pk, parent=None)
    return comment.order_by('-comment_time')