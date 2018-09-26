from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Profile
from .forms import LoginForm, RegForm,ChangeNicknameForm,BindEmailForm,Changepassword,Forgetpassword
from django.core.mail import send_mail
import string,random,time

# 登录
def logins(request):
    # username = request.POST.get('username',None)
    # password = request.POST.get('password',None)
    # user = authenticate(request,username=username,password=password)
    # referer = request.META.get('HTTP_REFERER',reverse('home'))
    # if user is not None:
    #     login(request,user)
    #     return redirect(referer)
    # else:
    #     return render(request,'error.html',{'message':'用户未登录，请先登录','redirect_to':referer})
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            login(request,user)
            return redirect(request.GET.get('from',reverse('home')))
            # username = login_form.cleaned_data['username']
            # password = login_form.cleaned_data['password']
            # user = authenticate(request, username=username, password=password)
            # if user is not None:
            #     login(request,user)
            #     return redirect(request.GET.get('from',reverse('home')))
            # else:
            #     login_form.add_error(None, '用户名或密码不正确')
    else:
        login_form = LoginForm()
    context = {}
    context['login_form'] = login_form
    return render(request,'user/login.html',context)

# 注册
def register(request):
    if request.method == "POST":
        reg_form = RegForm(request.POST,request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['passwords']
            user = User.objects.create_user(username,email,password)
            user.save()
            # 清除ｓｅｓｓｉｏｎ
            del request.session['register_code']
            # 登录用户
            user = authenticate(username=username,password=password)
            login(request,user)
            return redirect(request.GET.get('from',reverse('home')))
    else:
        reg_form = RegForm()
    context = {}
    context['reg_form'] = reg_form
    return render(request,'user/register.html',context)

# 未登录点赞处理
def login_form(request):
    data = {}
    login_form = LoginForm(request.POST)
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

# 退出登录
def login_out(request):
    logout(request)
    return redirect(request.GET.get('form',reverse('home')))

# 用户个人信息
def user_infor(request):
    context = {}
    return render(request,'user/user_infor.html',context)

# 修改昵称
def change_nickname(request):
    return_to = request.GET.get('from',reverse('home'))
    if request.method == 'POST':
        nickname_form = ChangeNicknameForm(request.POST,user = request.user)
        if nickname_form.is_valid():
            nickname = nickname_form.cleaned_data['new_nickname']
            profile,create = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname
            profile.save()
            return redirect(return_to)
    else:
        nickname_form = ChangeNicknameForm()
    context= {}
    context['page_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '修改'
    context['form'] = nickname_form
    context['return_back_url'] = return_to
    return render(request,'form.html',context)

# 绑定邮箱
def bind_email(request):
    return_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        email_form = BindEmailForm(request.POST, request=request)
        print(email_form)
        if email_form.is_valid():
            emails = email_form.cleaned_data['email']
            print(emails)
            request.user.email = emails
            request.user.save()
            # 清除ｓｅｓｓｉｏｎ
            del request.session['bind_email_codes']
            return redirect(return_to)
    else:
        email_form = BindEmailForm()
    context = {}
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_text'] = '绑定'
    context['form'] = email_form
    context['return_back_url'] = return_to
    return render(request, 'user/bind_email.html', context)

# 发送验证码
def send_email_code(request):
    email = request.GET.get('email','')
    send_for = request.GET.get('send_for','')
    data = {}
    if email != '':
        #生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits,4))
        # 将验证码保存在session中
        now = int(time.time())
        send_code_time = request.session.get('send_code_time',0)
        if now - send_code_time <= 30:
            data['status'] = 'ERROR'
        else:
            # request.session['bind_email_codes'] = code
            request.session[send_for] = code
            request.session['send_code_time'] = now

            #发送邮件
            send_mail(
                '绑定邮箱',
                '验证码：{}'.format(code),
                '2224268262@qq.com',
                [email],
                fail_silently=False,
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

# 修改密码
def change_password(request):
    return_to = reverse('home')
    if request.method == "POST":
        change_form = Changepassword(request.POST,user=request.user)
        if change_form.is_valid():
            user = request.user
            old_password = change_form.cleaned_data['old_password']
            newpassword = change_form.cleaned_data['newpassword']
            user.set_password(newpassword)
            user.save()
            logout(request)
            return redirect(return_to)
    else:
        change_form = Changepassword()
    context = {}
    context['page_title'] = '修改密码'
    context['form_title'] = '修改密码'
    context['submit_text'] = '修改'
    context['form'] = change_form
    context['return_back_url'] = return_to
    return render(request, 'form.html', context)

# 忘记密码
def forget_password(request):
    return_to = reverse('home')
    if request.method == 'POST':
        forgetpass_form = Forgetpassword(request.POST, request=request)
        if forgetpass_form.is_valid():
            email = forgetpass_form.cleaned_data['email']
            new_password = forgetpass_form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            # 清除ｓｅｓｓｉｏｎ
            del request.session['forget_password']
            return redirect(return_to)
    else:
        forgetpass_form = Forgetpassword()
    context = {}
    context['page_title'] = '忘记密码'
    context['form_title'] = '忘记密码'
    context['submit_text'] = '重置'
    context['form'] = forgetpass_form
    context['return_back_url'] = return_to
    return render(request, 'user/forget_password.html', context)
