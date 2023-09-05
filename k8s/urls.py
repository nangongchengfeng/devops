# -*- coding: utf-8 -*-
# @Time    : 2023/9/5 16:33
# @Author  : 南宫乘风
# @Email   : 1794748404@qq.com
# @File    : urls.py
# @Software: PyCharm
from django.urls import re_path

from k8s import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    re_path('^node/$', views.node,name='node'),
]