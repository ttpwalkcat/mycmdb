from django.contrib import admin

# Register your models here.

from . import models

admin.site.register(models.Users)
admin.site.register(models.ConfirmString)