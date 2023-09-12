# -*- coding: utf-8 -*-
# @Time    : 2023/9/5 16:36
# @Author  : 南宫乘风
# @Email   : 1794748404@qq.com
# @File    : urls.py
# @Software: PyCharm
from django.urls import re_path

from workload import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    re_path('^deployment/$', views.deployment, name='deployment'),
    re_path('^deployment_api/$', views.deployment_api, name='deployment_api'),
]
