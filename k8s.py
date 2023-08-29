# -*- coding: utf-8 -*-
# @Time    : 2023/8/28 22:05
# @Author  : 南宫乘风
# @Email   : 1794748404@qq.com
# @File    : k8s.py
# @Software: PyCharm

import os
from kubernetes import client, config

config.load_kube_config("k8s.yml")  # 指定kubeconfig配置文件
apps_api = client.AppsV1Api()  # 资源接口类实例化
core_api = client.CoreV1Api()  # namespace,pod,service,pv,pvc


# networking_api = client.NetworkingV1beta1Api()  # ingress
# storage_api = client.StorageV1Api()  # storage_class
# for dp in apps_api.list_deployment_for_all_namespaces().items:
#     print(dp)

# 查询一个 deployment
def deploy_get():
    namespace = "default"
    name = "api-test"
    try:
        resp = apps_api.read_namespaced_deployment(namespace=namespace, name=name)
        # print(resp)
        print("查询成功")
    except Exception as e:
        status = getattr(e, "status")
        if status == 404:
            print("没找到")
        elif status == 403:
            print("没权限")


# 创建一个deployment

def deploy_create():
    namespace = "default"
    name = "api-test"
    replicas = 3
    labels = {'a': '1', 'b': '2'}  # 不区分数据类型，都要加引号
    image = "nginx"
    body = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=name),
        spec=client.V1DeploymentSpec(
            replicas=replicas,
            selector={'matchLabels': labels},
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=labels),
                spec=client.V1PodSpec(
                    containers=[client.V1Container(
                        name="web",
                        image=image
                    )]
                )
            ),
        )
    )
    try:
        apps_api.create_namespaced_deployment(namespace=namespace, body=body)
    except Exception as e:
        status = getattr(e, "status")
        if status == 400:
            print(e)
            print("格式错误")
        elif status == 403:
            print("没权限")


# 删除一个deployment
def deploy_delete():
    namespace = "default"
    name = "api-test"
    body = client.V1DeleteOptions()
    try:
        apps_api.delete_namespaced_deployment(namespace=namespace, name=name, body=body)
    except Exception as e:
        status = getattr(e, "status")
        if status == 404:
            print("没找到")
        elif status == 403:
            print("没权限")
        elif status == 409:
            print("冲突")


def svc_get():
    # 查询
    for svc in core_api.list_namespaced_service(namespace="default").items:
        print(svc.metadata.name)



def svc_delete():
    namespace = "default"
    name = "api-test"
    body = client.V1DeleteOptions()
    try:
        core_api.delete_namespaced_service(namespace=namespace, name=name, body=body)
    except Exception as e:
        status = getattr(e, "status")
        if status == 404:
            print("没找到")
        elif status == 403:
            print("没权限")
        elif status == 409:
            print("冲突")

def svc_create():
    namespace = "default"
    name = "api-test"
    selector = {'a': '1', 'b': '2'}  # 不区分数据类型，都要加引号
    port = 80
    target_port = 80
    type = "NodePort"
    body = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(
            name=name
        ),
        spec=client.V1ServiceSpec(
            selector=selector,
            ports=[client.V1ServicePort(
                port=port,
                target_port=target_port
            )],
            type=type
        )
    )
    try:
        core_api.create_namespaced_service(namespace=namespace, body=body)
    except Exception as e:
        status = getattr(e, "status")
        if status == 400:
            print(e)
            print("格式错误")
        elif status == 403:
            print("没权限")

def svc_update():
    namespace = "default"
    name = "api-test"
    body = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(
            name=name
        ),
        spec=client.V1ServiceSpec(
            selector={'a': '1', 'b': '2'},
            ports=[client.V1ServicePort(
                port=80,
                target_port=8080
            )],
            type="NodePort"
        )
    )
    try:
        core_api.patch_namespaced_service(namespace=namespace, name=name, body=body)
    except Exception as e:
        status = getattr(e, "status")
        if status == 400:
            print(e)
            print("格式错误")
        elif status == 403:
            print("没权限")


if __name__ == '__main__':
    svc_update()