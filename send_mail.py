import os
from django.core.mail import send_mail

os.environ['DJANGO_SETTINGS_MODULE'] = 'login_register.settings'

if __name__ == '__main__':
    send_mail(
        '测试邮件',
        '欢迎访问！',
        'ttpwalkcat@163.com',
        ['ttpwalkcat@163.com'],
    )