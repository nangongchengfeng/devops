# -*- coding: utf-8 -*-
# @Time    : 2023/8/28 23:10
# @Author  : 南宫乘风
# @Email   : 1794748404@qq.com
# @File    : k8s.py
# @Software: PyCharm
# 登录认证检查
from kubernetes import client, config
import os


def auth_check(auth_type, str):
    if auth_type == "token":
        token = str
        configuration = client.Configuration()
        configuration.host = "https://192.168.102.30:6443"  # APISERVER地址
        configuration.ssl_ca_cert = os.path.join('kubeconfig', 'ca.crt')
        configuration.verify_ssl = True  # 启用证书验证
        configuration.api_key = {"authorization": "Bearer " + token}  # 指定Token字符串
        client.Configuration.set_default(configuration)
        try:
            core_api = client.CoreApi()
            core_api.get_api_versions()  # 查询资源测试
            return True
        except Exception as e:
            print(e)
            return False
    elif auth_type == "kubeconfig":
        random_str = str
        file_path = os.path.join('kubeconfig', random_str)
        config.load_kube_config(r"%s" % file_path)
        try:
            core_api = client.CoreApi()
            core_api.get_api_versions()  # 查询资源测试
            return True
        except Exception:
            return False
