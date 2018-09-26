from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
import threading
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Context,loader
from django.core.mail import EmailMultiAlternatives

class SendMail(threading.Thread):
    def __init__(self,subject, text,email,fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)
    def run(self):
        send_mail(
            self.subject,
            self.text,
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=self.fail_silently
        )

class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    # 这一条评论是谁写的
    user = models.ForeignKey(User,related_name="comments",on_delete=models.CASCADE)
    # 记录评论是基于哪一条评论开始的，也就是最顶级的回复
    root = models.ForeignKey('self',null=True,on_delete=models.DO_NOTHING,related_name="root_comment")
    # 回复第一条评论
    parent = models.ForeignKey('self',null=True,related_name="parent_comment",on_delete=models.CASCADE)
    # 回复谁
    reply_to = models.ForeignKey(User,null=True,related_name="replies",on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    def send_mail(self):
        # 发送邮件通知

        if self.parent is None:
            # 评论我的博客
            subject = '有人评论你的博客'
            email = self.content_object.get_email()
        else:
            # 评论你的回复
            subject = '有人回复了你的评论'
            email = self.reply_to.email

        if email != '':
            text = self.text + '\n' + self.content_object.get_url()
            send_mail = SendMail(subject,text,email)
            send_mail.start()

            # context = {
            #     'url':self.content_object.get_url(),
            #     'comment_text': self.text
            # }
            # print(context)
            # html = loader.get_template('comment/mail.html')
            #
            # message = html.render(context)
            # send_mail = EmailMultiAlternatives(subject,message,email)
            # send_mail.attach_alternative(message,"text/html")
            # # print(message)
            # # send_mail = SendMail(subject,message,email)
            # send_mail.send()


    class Meta:
        ordering = ['-comment_time']

# class Reply(models.Model):
#     comment = models.ForeignKey(Comment,on_delete=models.CASCADE)

