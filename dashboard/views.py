import hashlib
import os
import random

from django.http import JsonResponse
from django.shortcuts import render
from devops import k8s
from utils.LogHandler import log


# Create your views here.
def index(request):
    return render(request, 'index.html')


def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        token = request.POST.get("token", None)
        if token:
            log.info("token认证 %s" % token)
            if k8s.auth_check('token', token):
                code = 0
                msg = "认证成功"
            else:
                code = 1
                msg = "Token无效！"
        else:
            file_obj = request.FILES.get("file")
            random_str = hashlib.md5(str(random.random()).encode()).hexdigest()
            file_path = os.path.join('kubeconfig', random_str)
            try:
                with open(file_path, 'w', encoding='utf8') as f:
                    data = file_obj.read().decode()  # bytes转str
                    f.write(data)
            except Exception:
                code = 1
                msg = "文件类型错误！"
            if k8s.auth_check('kubeconfig', random_str):
                code = 0
                msg = "认证成功"
            else:
                code = 1
                msg = "认证文件无效！"
        res = {'code': code, 'msg': msg}
        log.info("认证结果 %s" % res)
        return JsonResponse(res)
