# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import models

# 基准模型，定义建表必备字段
class Basemodel(models.Model):
    '''
           基础表(抽象类)
        '''
    create_time = models.DateTimeField(auto_now_add=True,  verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    remark = models.TextField(default='', null=True, blank=True, verbose_name='备注')

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ['-id']