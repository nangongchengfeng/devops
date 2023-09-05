import hashlib
import os
import random

from django.http import JsonResponse
from django.shortcuts import render, redirect
from kubernetes import client, config
from devops import k8s
from utils.LogHandler import log


@k8s.self_login_required  # 从k8s.py中导入自定义登录认证装饰器
def index(request):
    """
    首页
    :param request:
    :return:
    """
    return render(request, 'index.html')


def login(request):
    """
    登录认证
    :param request:
    :return:
    """
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        # 获取认证类型
        token = request.POST.get("token", None)
        log.info("认证类型 %s" % token)
        # 判断认证类型,如果是token认证，直接调用k8s.auth_check()方法  如果是kubeconfig认证，先将文件写入本地，再调用k8s.auth_check()方法
        # token认证有值，kubeconfig认证无值
        if token:
            log.info("token认证 %s" % token)
            if k8s.auth_check('token', token):
                code = 0
                msg = "认证成功"
                # 认证成功后，将认证信息写入session
                request.session['is_login'] = True
                request.session['auth_type'] = "token"
                request.session['token'] = token
            else:
                code = 1
                msg = "Token无效！"
        else:
            # 获取文件对象
            file_obj = request.FILES.get("file")
            # 生成随机字符串
            random_str = hashlib.md5(str(random.random()).encode()).hexdigest()
            # 拼接文件路径
            file_path = os.path.join('kubeconfig', random_str)
            try:
                # 将文件写入本地
                with open(file_path, 'w', encoding='utf8') as f:
                    data = file_obj.read().decode()  # bytes转str
                    f.write(data)
            # 如果文件类型错误，捕获异常
            except Exception:
                code = 1
                msg = "文件类型错误！"
            # 如果文件类型正确，调用k8s.auth_check()方法
            if k8s.auth_check('kubeconfig', random_str):
                code = 0
                msg = "认证成功"
                # 认证成功后，将认证信息写入session
                request.session['is_login'] = True
                request.session['auth_type'] = "kubeconfig"
                request.session['token'] = random_str
            else:
                code = 1
                msg = "认证文件无效！"
        res = {'code': code, 'msg': msg}
        log.info("认证结果 %s" % res)
        # 返回认证结果
        return JsonResponse(res)


def logout(request):
    """
    注销用户
    :param request:
    :return:
    """
    log.info("注销用户")
    request.session.clear()
    return redirect(login)


def namespace_api(request):
    """
    获取namespace列表
    :param request:
    :return:
    """
    if request.method == 'GET':

        # 获取认证类型
        auth_type = request.session.get('auth_type', None)
        # 获取认证信息
        token = request.session.get('token', None)
        # 调用k8s.load_auth_config()方法
        k8s.load_auth_config(auth_type, token)

        # 获取namespace列表 对象实例化
        core_api = client.CoreV1Api()
        data = []
        try:
            # 遍历namespace列表
            for ns in core_api.list_namespace().items:
                name = ns.metadata.name
                labels = ns.metadata.labels
                creation_time = ns.metadata.creation_timestamp
                print(name, labels, creation_time)
                namespace = {'name': name, 'labels': labels, 'creation_time': creation_time}
                data.append(namespace)
            code = 0
            msg = "获取namespace列表成功"
            count = len(data)
            res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        except Exception as e:
            status = getattr(e, 'status', None)
            if status == 403:
                msg = "没有访问权限"
            else:
                msg = "获取namespace列表失败"
            code = 1
            res = {'code': code, 'msg': msg}
            # 返回失败信息

        # 返回namespace列表
        log.info("获取namespace列表 %s" % res)
        return JsonResponse(res)
    # return None


