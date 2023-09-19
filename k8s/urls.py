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
    re_path('^node/$', views.node, name='node'),
    re_path('^node_api/$', views.node_api, name='node_api'),
    re_path('^node_details/$', views.node_details, name="node_details"),
    re_path('^node_details_pod_list/$', views.node_details_pod_list, name="node_details_pod_list"),
    re_path('^pv/$', views.pv, name='pv'),
    re_path('^pv_api/$', views.pv_api, name='pv_api'),
    re_path('^pv_create/$', views.pv_create, name='pv_create'),
]
