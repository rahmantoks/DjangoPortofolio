from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/snake/$', consumers.SnakeConsumer.as_asgi()),
    # Add more WebSocket consumers as needed
]
