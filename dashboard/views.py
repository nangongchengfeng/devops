import hashlib
import os
import random

from django.http import JsonResponse, QueryDict
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
     # 命名空间选择和命名空间表格使用
    :param request:
    :return:
    """
    # 获取认证类型
    auth_type = request.session.get('auth_type', None)
    # 获取认证信息
    token = request.session.get('token', None)
    # 调用k8s.load_auth_config()方法
    k8s.load_auth_config(auth_type, token)

    # 获取namespace列表 对象实例化
    core_api = client.CoreV1Api()
    if request.method == 'GET':

        search_key = request.GET.get('search_key', None)
        data = []
        try:
            # 遍历namespace列表
            for ns in core_api.list_namespace().items:
                name = ns.metadata.name
                labels = ns.metadata.labels
                create_time = k8s.dt_format(ns.metadata.creation_timestamp)
                print(name, labels, create_time)
                namespace = {'name': name, 'labels': labels, 'create_time': create_time}
                if search_key:
                    if search_key in name:
                        data.append(namespace)
                else:
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
            log.error("获取namespace列表 %s" % res)
            # 返回失败信息
        count = len(data)
        # 分页
        #  "GET /namespace_api/?page=2&limit=10
        # 参数page表示当前页数，参数limit表示每页显示的条数
        if request.GET.get('page'):
            """
            page number 当前页数
            limit number 每页显示条数
            """
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit'))
            # 计算每页的起始位置和结束位置
            start = (page - 1) * limit
            # 计算每页的结束位置
            end = page * limit
            # 切片
            data = data[start:end]

        res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        # 返回namespace列表
        log.info("获取namespace列表 %s" % res)
        return JsonResponse(res)
    elif request.method == "POST":
        name = request.POST['name']

        # 判断命名空间是否存在
        for ns in core_api.list_namespace().items:
            if name == ns.metadata.name:
                res = {'code': 1, "msg": "命名空间已经存在！"}
                return JsonResponse(res)

        body = client.V1Namespace(
            api_version="v1",
            kind="Namespace",
            metadata=client.V1ObjectMeta(
                name=name
            )
        )
        try:
            core_api.create_namespace(body=body)
            code = 0
            msg = "创建命名空间成功."
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "没有访问权限！"
            else:
                msg = "创建失败！"
        res = {'code': code, 'msg': msg}
        log.info("创建命名空间 %s" % res)
        return JsonResponse(res)

    elif request.method == "DELETE":
        """
        删除namespace
        """
        request_data = QueryDict(request.body)
        log.info("删除namespace %s" % request_data)
        name = request_data.get("name")
        try:
            core_api.delete_namespace(name)
            code = 0
            msg = "删除成功."
            log.info("删除namespace %s 成功" % name)
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "没有删除权限"
            else:
                msg = "删除失败！"
            log.error("删除namespace %s 失败" % name)
        res = {'code': code, 'msg': msg}
        return JsonResponse(res)


def namespace(request):
    return render(request, 'k8s/namespace.html')
