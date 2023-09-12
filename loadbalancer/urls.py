# -*- coding: utf-8 -*-
# @Time    : 2023/9/5 16:36
# @Author  : 南宫乘风
# @Email   : 1794748404@qq.com
# @File    : urls.py
# @Software: PyCharm
from django.urls import re_path

from loadbalancer import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    re_path('^service/$', views.service, name='service'),
    re_path('^service_api/$', views.service_api, name='service_api'),
    re_path('^ingress/$', views.ingress, name='ingress'),
    re_path('^ingress_api/$', views.ingress_api, name='ingress_api'),

]
