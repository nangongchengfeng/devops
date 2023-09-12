# -*- coding: utf-8 -*-
# @Time    : 2023/9/5 16:36
# @Author  : 南宫乘风
# @Email   : 1794748404@qq.com
# @File    : urls.py
# @Software: PyCharm
from django.urls import re_path

from storage import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    re_path('^pvc/$', views.pvc, name='pvc'),
    re_path('^pvc_api/$', views.pvc_api, name='pvc_api'),
    re_path('^configmap/$', views.configmap, name='configmap'),
    re_path('^configmap_api/$', views.configmap_api, name='configmap_api'),
    re_path('^secret/$', views.secret, name='secret'),
    re_path('^secret_api/$', views.secret_api, name='secret_api'),
]
