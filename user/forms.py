from django import forms
from django.contrib import auth
from django.urls import reverse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User


# 登录表单
class LoginForm(forms.Form):
    # required = True   提示此项表单必须填写
    username_or_email = forms.CharField(label='用户名',
                               widget=forms.TextInput(attrs={'class':'form-control','placeholder':"请输入用户名或邮箱"}))
    password = forms.CharField(label='密码',
                               widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':"请输入密码"}))

    # 对填写的数据进行验证
    def clean(self):
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']

        user = auth.authenticate( username=username_or_email, password=password)
        if user is None:
            # 使用邮箱登录
            if User.objects.filter(email = username_or_email).exists():
                username = User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username,password=password)
                if not user is None:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
            raise forms.ValidationError('用户名或密码不正确')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data

# 注册表单
class RegForm(forms.Form):
    username = forms.CharField(label='用户名',max_length=15,min_length=3,
                               widget=forms.TextInput(attrs={'class':'form-control','placeholder':"请输入3-15位用户名"}))
    email = forms.EmailField(label="邮箱",
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "请输入邮箱"}))
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '点击发送验证码'}))
    password = forms.CharField(label='密码',min_length=6,
                               widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':"请输入密码"}))
    passwords = forms.CharField(label='确认密码',min_length=6,
                               widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':"请确认密码"}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(RegForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断验证码
        code = self.request.session.get('register_code', '')
        ver_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == ver_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email = email).exists():
            raise forms.ValidationError('邮箱已存在')
        return email

    def clean_passwords(self):
        password = self.cleaned_data['password']
        passwords = self.cleaned_data['passwords']
        if password != passwords:
            raise forms.ValidationError('两次密码输入不一致')
        return passwords

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code','').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code

# 修改昵称表单
class ChangeNicknameForm(forms.Form):
    new_nickname = forms.CharField(
        label='新昵称',max_length=20,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':"请输入昵称"}))

    def __init__(self,*args,**kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangeNicknameForm,self).__init__(*args,**kwargs)

    def clean(self):
        #判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')
        return self.cleaned_data

    def clean_newnickname(self):
        new_nickname = self.cleaned_data['new_nickname',''].strip()
        print(new_nickname)
        if new_nickname =='':
            raise forms.ValidationError('昵称不能为空')
        return new_nickname

# 绑定邮箱表单
class BindEmailForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(
            attrs={'class':'form-control','placeholder':'请输入正确的邮箱'}
        )
    )

    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class':'form-control','placeholder':'点击发送验证码'}
        )
    )

    def __init__(self,*args,**kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(BindEmailForm,self).__init__(*args,**kwargs)
    #
    def clean(self):
        #判断用户是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('用户尚未登录')

        #判断用户是否已经绑定邮箱
        if self.request.user.email != '':
            raise forms.ValidationError('你已经绑定邮箱')

        #判断验证码
        code = self.request.session.get('bind_email_codes','')
        ver_code = self.cleaned_data.get('verification_code','')
        if not(code != '' and code == ver_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已经绑定')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code','').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code

# 修改密码表单
class  Changepassword(forms.Form):
    old_password = forms.CharField(
        label='旧密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "请输入密码"})
    )
    newpassword = forms.CharField(
        label='新密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "请输入密码"})
    )
    newpasswords = forms.CharField(
        label='确认新密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "请输入密码"})
    )

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(Changepassword, self).__init__(*args, **kwargs)

    def clean(self):
        new_password = self.cleaned_data.get('newpassword','')
        new_passwords = self.cleaned_data.get('newpasswords','')
        if new_password != new_passwords or new_password == "":
            raise forms.ValidationError('两次密码输入不一致')
        return self.cleaned_data

    # 验证旧的密码
    def clean_oldpassword(self):
        old_password = self.cleaned_data.get('old_password','')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('旧密码错误')
        return self.old_password

# 忘记密码表单，通过邮箱检验验证码找回
class Forgetpassword(forms.Form):
    email = forms.EmailField(label='用户名',
                               widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "请输入绑定的邮箱"}))

    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '点击发送验证码'}))
    new_password = forms.CharField(label='新密码',
                                   min_length=6,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "请输入新密码"}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(Forgetpassword, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱不存在')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code','').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        code = self.request.session.get('forget_password', '')
        ver_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == ver_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data