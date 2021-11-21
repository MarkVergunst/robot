from django.conf.urls import url

from butterrobot.consumers.arduino import ArduinoConsumer
from butterrobot.consumers.image import ImageConsumer

websocket_urlpatterns = [
    url(r'^ws/(?P<room_code>\w+)/$', ArduinoConsumer.as_asgi()),
    url(r'^ws/image/(?P<room_code>\w+)/$', ImageConsumer.as_asgi()),
]
