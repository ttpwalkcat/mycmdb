from django.shortcuts import render, redirect
from django.contrib.auth import login


from django.contrib.auth.decorators import login_required
from django.conf import settings
from . import models
from . import forms
import hashlib
import datetime

# Create your views here.

# 生成 hash code，用于密码加密、注册确认
def hash_code(s, salt='mysite'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update 方法只接收 bytes 类型
    return h.hexdigest()

# 注册确认
def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.username, now)
    models.ConfirmString.objects.create(code=code, user=user)
    return code

# 发送邮件
def send_email(email, code):
    from django.core.mail import EmailMultiAlternatives
    # subject = "来自%s的注册确认邮件" % {settings.APP_NAME}
    subject = "来自{}的注册邮件".format(settings.APP_NAME)
    text_content = '''欢迎注册，这里是QMY的站点！\
                    如果你看到这条消息，说明你的邮箱服务器不提供 HTML 链接功能，请联系管理员！ '''
    html_content = '''
                   <p>感谢注册，这里是QMY的站点！\
                   <p><a href="http://{}/accounts/confirm/?code={}" target=blank>请点击这里</a> 完成注册确认！</p>
                   <p>此链接有效期为{}天</p>
                   '''.format(settings.APP_HOST_PORT, code, settings.CONFIRM_DAYS)
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

# def index(request):
#     if not request.session.get('is_login', None):
#         return redirect('/accounts/')
#     return render(request, 'login/index.html')

def user_login(request):
    is_authenticated = request.user.is_authenticated
    if is_authenticated:        # 判断是否已登录，如果是直接进入 index 页面
        return redirect('/index/')

    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        err_message = '登录失败，用户名或密码错误！'

        if login_form.is_valid():        # 表单类(forms.Form) 自带的is_vaild() 方法完成数据验证
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')

            try:
                user_info = models.Users.objects.get(username=username)    # 尝试去数据库拿到 username 对应的对象，隐藏含义为，验证用户名是否存在
            except:                                                  # get() 用法：get(字段名=值)，字段名来自models 中定义的字段名
                # err_message = '用户不存在！'
                return render(request, 'login/login.html', locals()) # 如果验证不通过，返回一个包含先前数据的表单给前端页面，方便用户修改，下同
                                                                     # locals() 函数，返回当前所有的本地变量字典，可以作为 render 函数的数据字典参数值，无需手工构造
            if not user_info.has_confirmed:
                err_message = "用户未通过邮件确认！"
                return render(request, 'login/login.html', locals())

            if not user_info.status:
                err_message = "用户已被禁用！"
                return render(request, 'login/login.html', locals())

            if hash_code(password) == user_info.password:
                # print(username, password)
                # 使用 Django 默认的 login 方法进行登录标记
                user_info.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user_info)
                # request.session['is_login'] = True
                # request.session['user_id'] = user.id
                # request.session['user_name'] = user.username
                request.session.set_expiry(1800)        # 设置会话有效时间，单位秒
                return redirect(request.GET.get('next', '/assets/index/'))    # 使用 GET.get()方法而不是 GET[''] 获取 next 值，防止取不到值报错
            else:
                # err_message = '密码不正确'
                return render(request, 'login/login.html', locals())
        else:
            return render(request, 'login/login.html', locals())

    login_form = forms.UserForm()                            # 对于非POST方法发送数据时，比如GET方法请求页面，返回空的表单，让用户可以填入数据
    return render(request, 'login/login.html', locals())

def register(request):
    # 当用户已登录时，跳转到 index 首页
    # if request.session.get('is_login', None):
    #     return redirect('/index/')

    if request.method == 'POST':
        # 如果已登录，尝试退出登录
        if request.user.is_authenticated:
            request.session.flush()

        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            realname = register_form.cleaned_data.get('realname')
            mobile = register_form.cleaned_data.get('mobile')
            sex = register_form.cleaned_data.get('sex')

            if password1 != password2:
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.Users.objects.filter(username=username)
                if same_name_user:
                    message = "用户名已存在"
                    return render(request, 'login/register.html', locals())
                same_email_user = models.Users.objects.filter(email=email)
                if same_email_user:
                    message = "该邮箱已注册"
                    return render(request, 'login/register.html', locals())
                same_mobile_user = models.Users.objects.filter(mobile=mobile)
                if same_mobile_user:
                    message = "该手机号已注册"
                    return render(request, 'login/register.html', locals())

                new_user = models.Users()
                new_user.username = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.realname = realname
                new_user.mobile = mobile
                new_user.sex = sex
                new_user.save()

                code = make_confirm_string(new_user)
                send_email(email, code)

                return redirect('/accounts/login/')
        else:
            return render(request, 'login/register.html', locals())

    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())

def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = "无效的确认请求!"
        return render(request, 'login/confirm.html', locals())

    create_time = confirm.create_time
    now = datetime.datetime.now()
    if now > create_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()        # 这里可以改成 update，添加状态字段
        message = "您的邮件已经过期！请重新注册！"
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.status = True
        confirm.user.save()
        confirm.delete()             # 同上
        message = "确认成功，请使用账户登录！"
        return render(request, 'login/confirm.html', locals())

# @login_required
def logout(request):
    # if not request.session.get('is_login', None):
    #     return redirect('/accounts/')
    # 通过装饰器 login_required 已经验证了登录状态，不再需要如上的自定义验证
    request.session.flush()

    # 或者，使用下面 手动清除方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']

    return redirect('/accounts/login/')

@login_required
def users_list(request):
    users = models.Users.objects.all()
    return render(request, 'users/users_list.html', locals())

@login_required
def users_add(request):
    return render(request, 'users/users_list.html', locals())


@login_required
def users_manager(request, user_id=None, disabled=None):
    """ 用户个人信息修改 """
    if user_id:
        user = models.Users.objects.get(pk=user_id)

        if request.method == "POST":
            # 判断是否 禁用用户
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.mobile = request.POST.get('mobile')
            user.realname = request.POST.get('realname')
            user.sex = request.POST.get('sex')
            user.status = request.POST.get('status')

            password = request.POST.get('password')
            # 因为没有解密方法，返回前端的密码为加密后密码，因此判断用户是否修改密码，直接对比password 字符串即可
            if password != user.password:
                user.password = hash_code(password)

            user.save()

        if disabled == "disabled":
            if user.username == "admin":
                message = "无法禁用管理员(admin)用户"
            else:
                user.status = False
                user.save()
            return redirect('/accounts/users_list/')
    else:
        message = "请求的用户不存在！"
        return redirect('/accounts/users_list/')
            # current_username = request.user.username
            # current_user = models.Users.objects.get(username=current_username)
            # if current_user.is_superuser:
            #     users = models.Users.objects.all()
            #     return render(request, 'users/users_list.html', locals())
            # else:
            #     message = "您没有管理用户的权限！"
            #     return message
            # users = models.Users.objects.all()
            # return render(request, 'users/users_list.html', locals())
    return render(request, 'users/user_info_manage.html', locals())

@login_required
def user_info(request, user_id=None):
    """ 查看、修改用户个人信息 """
    if not user_id:
        user_id = request.user.id
    user = models.Users.objects.get(pk=user_id)

    if request.method == "POST":
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.mobile = request.POST.get('mobile')
        user.realname = request.POST.get('realname')
        user.sex = request.POST.get('sex')
        user.save()

    return render(request, 'users/user_info.html', locals())

@login_required
def reset_password(request):
    username = request.user.username
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if new_password1 != new_password2:
            err_message = "两次输入密码不同！"
            return render(request, 'users/user_info.html', locals())
        try:
            user_info = models.Users.objects.get(username=username)
        except:
            err_message = '用户不存在！'
            return render(request, 'users/user_info.html', locals())
        if not user_info.has_confirmed:
            err_message = "用户未通过邮件确认！"
            return render(request, 'users/user_info.html', locals())

        if hash_code(old_password) == user_info.password:
            user_info.password = hash_code(new_password1)
            user_info.save()
        else:
            err_message = "原密码错误"

    return render(request, 'users/user_info.html', locals())




