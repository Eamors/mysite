from django.urls import path
from . import views

urlpatterns = [
    path('user_infor/', views.user_infor, name='user_infor'),#用户个人信息
    path('login/',views.logins,name="login"),#登录
    path('register/',views.register,name="register"),#注册
    path('login_form/',views.login_form,name="login_form"),#点赞时候没有登录
    path('login_out/',views.login_out,name='login_out'),#退出
    path('change_nickname/',views.change_nickname,name='change_nickname'),#修改昵称
    path('bind_email/',views.bind_email,name='bind_email'),#绑定邮箱
    path('send_email_code/',views.send_email_code,name='send_email_code'),#发送验证码
    path('change_password/',views.change_password,name='change_password'),#修改密码
    path('forget_password/',views.forget_password,name='forget_password'),#忘记密码
]