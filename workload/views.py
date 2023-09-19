from django.http import JsonResponse, QueryDict
from django.shortcuts import render
from kubernetes import client

from devops import k8s
from utils.LogHandler import log


# Create your views here.
def deployment(request):
    return render(request, 'workload/deployment.html')


def deployment_api(request):
    if request.method == 'GET':
        code = 0
        msg = ''
        auth_type = request.session.get("auth_type")
        token = request.session.get("token")
        k8s.load_auth_config(auth_type, token)
        apps_api = client.AppsV1Api()
        search_key = request.GET.get("search_key")
        namespace = request.GET.get("namespace")
        data = []
        try:
            for dp in apps_api.list_namespaced_deployment(namespace=namespace).items:
                name = dp.metadata.name
                namespace = dp.metadata.namespace
                replicas = dp.spec.replicas
                available_replicas = (0 if dp.status.available_replicas is None else dp.status.available_replicas)
                labels = dp.metadata.labels
                selector = dp.spec.selector.match_labels
                if len(dp.spec.template.spec.containers) > 1:
                    images = ""
                    n = 1
                    for c in dp.spec.template.spec.containers:
                        status = ("运行中" if dp.status.conditions[0].status == "True" else "异常")
                        image = c.image
                        images += "[%s]: %s / %s" % (n, image, status)
                        images += "<br>"
                        n += 1
                else:
                    status = (
                        "运行中" if dp.status.conditions[0].status == "True" else "异常")
                    image = dp.spec.template.spec.containers[0].image
                    images = "%s / %s" % (image, status)

                create_time = k8s.dt_format(dp.metadata.creation_timestamp)
                dp = {"name": name, "namespace": namespace, "replicas": replicas,
                      "available_replicas": available_replicas, "labels": labels, "selector": selector,
                      "images": images, "create_time": create_time}
                # 根据搜索值返回数据
                if search_key:
                    if search_key in name:
                        data.append(dp)
                else:
                    data.append(dp)
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

        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit'))
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]

        res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        log.info("获取deployment数据操作,返回数据为: %s" % res)
        return JsonResponse(res)
    elif request.method == "PUT":
        auth_type = request.session.get("auth_type")
        token = request.session.get("token")
        k8s.load_auth_config(auth_type, token)
        apps_api = client.AppsV1Api()
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        replicas = int(request_data.get("replicas"))
        try:
            body = apps_api.read_namespaced_deployment(name=name, namespace=namespace)
            current_replicas = body.spec.replicas
            min_replicas = 0
            max_replicas = 20
            if replicas > current_replicas and replicas < max_replicas:
                # body = body.spec.template.spec.containers[0].image = "nginx:1.17"
                body.spec.replicas = replicas  # 更新对象内副本值
                apps_api.patch_namespaced_deployment(name=name, namespace=namespace, body=body)
                msg = "扩容成功！"
                code = 0
            elif replicas < current_replicas and replicas > min_replicas:
                body.spec.replicas = replicas
                apps_api.patch_namespaced_deployment(name=name, namespace=namespace, body=body)
                msg = "缩容成功！"
                code = 0
            elif replicas == current_replicas:
                msg = "副本数一致！"
                code = 1
            elif replicas > max_replicas:
                msg = "副本数设置过大！请联系管理员操作。"
                code = 1
            elif replicas == min_replicas:
                msg = "副本数不能设置0！"
                code = 1
        except Exception as e:
            status = getattr(e, "status")
            if status == 403:
                msg = "你没有扩容/缩容权限！"
            else:
                msg = "扩容/缩容失败！"
            code = 1
        res = {"code": code, "msg": msg}
        log.info("扩容/缩容deployment数据操作,返回数据为: %s" % res)
        return JsonResponse(res)

    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        auth_type = request.session.get("auth_type")
        token = request.session.get("token")
        k8s.load_auth_config(auth_type, token)
        apps_api = client.AppsV1Api()
        try:
            apps_api.delete_namespaced_deployment(namespace=namespace, name=name)
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
        log.info("删除deployment数据操作,返回数据为: %s" % res)
        return JsonResponse(res)


def daemonset(request):
    return render(request, 'workload/daemonset.html')


def daemonset_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.load_auth_config(auth_type, token)
    apps_api = client.AppsV1Api()
    if request.method == "GET":
        search_key = request.GET.get("search_key")
        namespace = request.GET.get("namespace")
        data = []
        try:
            for ds in apps_api.list_namespaced_daemon_set(namespace).items:
                name = ds.metadata.name
                namespace = ds.metadata.namespace
                desired_number = ds.status.desired_number_scheduled
                available_number = ds.status.number_available
                labels = ds.metadata.labels
                selector = ds.spec.selector.match_labels
                containers = {}
                for c in ds.spec.template.spec.containers:
                    containers[c.name] = c.image
                create_time = k8s.dt_format(ds.metadata.creation_timestamp)

                ds = {"name": name, "namespace": namespace, "labels": labels, "desired_number": desired_number,
                      "available_number": available_number,
                      "selector": selector, "containers": containers, "create_time": create_time}

                # 根据搜索值返回数据
                if search_key:
                    if search_key in name:
                        data.append(ds)
                else:
                    data.append(ds)
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

        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit'))
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]

        res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        log.info("获取daemonset数据操作,返回数据为: %s" % res)
        return JsonResponse(res)

    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        try:
            apps_api.delete_namespaced_daemon_set(namespace=namespace, name=name)
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
        log.info("删除daemonset数据操作,返回数据为: %s" % res)
        return JsonResponse(res)


# statefulset 服务
def statefulset(request):
    return render(request, 'workload/statefulset.html')


def statefulset_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.load_auth_config(auth_type, token)
    apps_api = client.AppsV1Api()
    if request.method == "GET":
        search_key = request.GET.get("search_key")
        namespace = request.GET.get("namespace")
        data = []
        try:
            for sts in apps_api.list_namespaced_stateful_set(namespace).items:
                name = sts.metadata.name
                namespace = sts.metadata.namespace
                labels = sts.metadata.labels
                selector = sts.spec.selector.match_labels
                replicas = sts.spec.replicas
                ready_replicas = ("0" if sts.status.ready_replicas is None else sts.status.ready_replicas)
                # current_replicas = sts.status.current_replicas
                service_name = sts.spec.service_name
                containers = {}
                for c in sts.spec.template.spec.containers:
                    containers[c.name] = c.image
                create_time = k8s.dt_format(sts.metadata.creation_timestamp)

                sts = {"name": name, "namespace": namespace, "labels": labels, "replicas": replicas,
                       "ready_replicas": ready_replicas, "service_name": service_name,
                       "selector": selector, "containers": containers, "create_time": create_time}

                # 根据搜索值返回数据
                if search_key:
                    if search_key in name:
                        data.append(sts)
                else:
                    data.append(sts)
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

        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit'))
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]

        res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        log.info("获取statefulset数据操作,返回数据为: %s" % res)
        return JsonResponse(res)

    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        try:
            apps_api.delete_namespaced_stateful_set(namespace=namespace, name=name)
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
        log.info("删除statefulset数据操作,返回数据为: %s" % res)
        return JsonResponse(res)


# pod 服务
def pod(request):
    return render(request, 'workload/pod.html')


def pod_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.load_auth_config(auth_type, token)
    core_api = client.CoreV1Api()
    if request.method == "GET":
        search_key = request.GET.get("search_key")
        namespace = request.GET.get("namespace")
        data = []
        try:
            for po in core_api.list_namespaced_pod(namespace).items:
                name = po.metadata.name
                namespace = po.metadata.namespace
                labels = po.metadata.labels
                pod_ip = po.status.pod_ip

                containers = []  # [{},{},{}]
                status = "None"
                # 只为None说明Pod没有创建（不能调度或者正在下载镜像）
                if po.status.container_statuses is None:
                    status = po.status.conditions[-1].reason
                else:
                    for c in po.status.container_statuses:
                        c_name = c.name
                        c_image = c.image

                        # 获取重启次数
                        restart_count = c.restart_count

                        # 获取容器状态
                        c_status = "None"
                        if c.ready is True:
                            c_status = "Running"
                        elif c.ready is False:
                            if c.state.waiting is not None:
                                c_status = c.state.waiting.reason
                            elif c.state.terminated is not None:
                                c_status = c.state.terminated.reason
                            elif c.state.last_state.terminated is not None:
                                c_status = c.last_state.terminated.reason

                        c = {'c_name': c_name, 'c_image': c_image, 'restart_count': restart_count, 'c_status': c_status}
                        containers.append(c)

                create_time = k8s.dt_format(po.metadata.creation_timestamp)

                po = {"name": name, "namespace": namespace, "pod_ip": pod_ip,
                      "labels": labels, "containers": containers, "status": status,
                      "create_time": create_time}

                # 根据搜索值返回数据
                if search_key:
                    if search_key in name:
                        data.append(po)
                else:
                    data.append(po)
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

        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit'))
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]

        res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        log.info("获取pod数据操作,返回数据为: %s" % res)
        return JsonResponse(res)

    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        try:
            core_api.delete_namespaced_pod(namespace=namespace, name=name)
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
        log.info("删除pod数据操作,返回数据为: %s" % res)
        return JsonResponse(res)
