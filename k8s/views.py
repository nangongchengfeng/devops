from django.http import JsonResponse, QueryDict
from django.shortcuts import render, redirect
from kubernetes import client, config
from devops import k8s
from utils.LogHandler import log


# Create your views here.
def node(request):
    return render(request, 'k8s/node.html')


def node_api(request):
    """
    node列表 的详细信息 查询接口
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
        search_key = request.GET.get('search_key', None)
        data = []
        try:
            # 遍历namespace列表
            for node in core_api.list_node_with_http_info()[0].items:
                # 获取node的详细信息
                name = node.metadata.name
                # 标签
                labels = node.metadata.labels
                # 创建时间
                create_time = node.metadata.creation_timestamp
                # 准备就绪
                status = node.status.conditions[-1].status
                # 节点调度
                scheduler = ("是" if node.spec.unschedulable is None else "否")

                cpu = node.status.capacity['cpu']
                memory = node.status.capacity['memory']
                kebelet_version = node.status.node_info.kubelet_version
                cri_version = node.status.node_info.container_runtime_version

                node = {"name": name, "labels": labels, "status": status,
                        "scheduler": scheduler, "cpu": cpu, "memory": memory,
                        "kebelet_version": kebelet_version, "cri_version": cri_version,
                        "create_time": create_time}
                # 根据搜索值返回数据

                if search_key:
                    if search_key in name:
                        data.append(node)
                else:
                    data.append(node)
            code = 0
            msg = "获取Node列表成功"
            count = len(data)
            res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        except Exception as e:
            status = getattr(e, 'status', None)
            if status == 403:
                msg = "没有访问权限"
            else:
                msg = "获取Node列表失败"
            code = 1
            res = {'code': code, 'msg': msg}
            log.error("获取Node列表 %s" % res)
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
        log.info("获取Node列表 %s" % res)
        return JsonResponse(res)





def pv(request):
    return render(request, 'k8s/pv.html')



def pv_api(request):
    # 命名空间选择和命名空间表格使用
    if request.method == "GET":
        code = 0
        msg = ""
        auth_type = request.session.get("auth_type")
        token = request.session.get("token")
        k8s.load_auth_config(auth_type, token)
        core_api = client.CoreV1Api()
        search_key = request.GET.get("search_key")
        data = []
        try:
            for pv in core_api.list_persistent_volume().items:
                name = pv.metadata.name
                capacity = pv.spec.capacity["storage"]
                access_modes = pv.spec.access_modes
                reclaim_policy = pv.spec.persistent_volume_reclaim_policy
                status = pv.status.phase
                if pv.spec.claim_ref is not None:
                    pvc_ns = pv.spec.claim_ref.namespace
                    pvc_name = pv.spec.claim_ref.name
                    pvc = "%s / %s" % (pvc_ns, pvc_name)
                else:
                    pvc = "未绑定"
                storage_class = pv.spec.storage_class_name
                create_time = pv.metadata.creation_timestamp
                pv = {"name": name, "capacity": capacity, "access_modes":access_modes,
                             "reclaim_policy":reclaim_policy , "status":status, "pvc":pvc,
                            "storage_class":storage_class,"create_time": create_time}
                # 根据搜索值返回数据
                if search_key:
                    if search_key in name:
                        data.append(pv)
                else:
                    data.append(pv)
                code = 0
                msg = "获取数据成功"
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "没有访问权限"
            else:
                msg = "获取数据失败"
        count = len(data)

        # 分页
        page = int(request.GET.get('page',1))
        limit = int(request.GET.get('limit'))
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]

        res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        log.info("获取pv列表 %s" % res)
        return JsonResponse(res)

    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        auth_type = request.session.get("auth_type")
        token = request.session.get("token")
        k8s.load_auth_config(auth_type, token)
        core_api = client.CoreV1Api()
        try:
            core_api.delete_persistent_volume(name)
            code = 0
            msg = "删除成功."
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "没有删除权限"
            else:
                msg = "删除失败！"
        res = {'code': code, 'msg': msg}
        log.info("删除pv %s" % res)
        return JsonResponse(res)