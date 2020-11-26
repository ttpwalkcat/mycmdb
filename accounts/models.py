from django.db import models
from datetime import date
from utils.basemodels import Basemodel
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# 用户表
class Users(AbstractBaseUser, Basemodel):

    # gender = (
    #     ('male', "男"),
    #     ('femail', "女")
    # )
    gender = (
        (1, "男"),
        (0, "女")
    )

    username = models.CharField(max_length=128, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=256, verbose_name="密码")
    email = models.EmailField(unique=True, verbose_name="电子邮箱")
    mobile = models.BigIntegerField(unique=True, verbose_name="手机号码")
    realname = models.CharField(max_length=128, verbose_name="真实姓名")
    # sex = models.CharField(max_length=6, choices=gender, default="男")
    sex = models.SmallIntegerField(choices=gender, default="男", verbose_name="性别")
    has_confirmed = models.BooleanField(default=False)
    status = models.BooleanField(default=False)

    # Admin
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    # 如果使用 Django 提供的 login()方法，必须添加last_login 字段，否则会报错"fields do not exist"
    # 或者，设置当前 class 继承 AbstractUser，from django.contrib.auth.models import AbstractUser
    last_login = models.DateTimeField(auto_now_add=True, verbose_name="最后登录时间")

    USERNAME_FIELD = 'email'

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["-create_time"]        # 设置默认排序方式，按照 c_time 倒序排序，也就是最近的最先显示
        verbose_name = "用户"
        verbose_name_plural = "用户"


# 注册确认表
class ConfirmString(Basemodel):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('Users', on_delete=models.CASCADE)
    confirm_type = models.SmallIntegerField(verbose_name="注册确认类型：1-邮件；2-手机", default=1)

    def __str__(self):
        return self.user.username + ":   " + self.code

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "确认码"
        verbose_name_plural = "确认码"