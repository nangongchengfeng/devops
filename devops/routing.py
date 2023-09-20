from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from django.urls import re_path
from devops.consumers import StreamConsumer

application = ProtocolTypeRouter({

})
