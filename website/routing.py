from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.conf.urls import url

from DBModel.consumers import *

ws_urlpatterns = [
    url(r'^wslogin$', LoginConsumer),
    url(r'^wsapp$', AppConsumer),
]

application = ProtocolTypeRouter({
    "websocket" : AuthMiddlewareStack(
        URLRouter(ws_urlpatterns)
    )
})