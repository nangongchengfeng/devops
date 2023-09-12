from django.shortcuts import render


def service(request):
    return render(request, 'loadbalancer/service.html')


def service_api(request):
    return None


def ingress(request):
    return render(request, 'loadbalancer/ingress.html')


def ingress_api(request):
    return None