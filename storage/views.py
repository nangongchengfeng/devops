from django.shortcuts import render

# Create your views here.
def pvc(request):
    return render(request, 'loadbalancer/pvc.html')


def pvc_api(request):
    return None


def configmap(request):
    return render(request, 'loadbalancer/configmap.html')


def configmap_api(request):
    return None


def secret(request):
    return render(request, 'loadbalancer/secret.html')


def secret_api(request):
    return None