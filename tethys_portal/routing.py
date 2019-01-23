
from channels.http import AsgiHandler
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from django.conf.urls import url
import tethys_portal.consumers as consumers

http_urlpatterns = [
    url(r'^asynchttp$', consumers.BasicHttpConsumer),
    url(r"", AsgiHandler),  # other sync urls go to sync handler
]



application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    'http': AuthMiddlewareStack(
        URLRouter(
            http_urlpatterns
        )
    ),
})

