import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import rfid_project.routing  # thay 'your_app' bằng tên ứng dụng của bạn

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rfid_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            rfid_project.routing.websocket_urlpatterns
        )
    ),
})
