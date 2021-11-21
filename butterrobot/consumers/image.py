import json
import time
from datetime import datetime

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.core.cache import cache
from PIL import Image
from io import BytesIO

class ImageConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = 'room_%s' % self.room_name
        self.current_user = self.scope['user']

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print("Disconnected ImageConsumer")
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        """
        Receive data from WebSocket.
        """
        key = f"BMP_HEADER"
        # TODO write every 5 seconds rewrite

        bmp_header = cache.get(key)
        write_file = False

        timelap = cache.get("TIMELAP")
        if cache.get("TIMELAP") is None:
            timelap = int(time.time())
            cache.set("TIMELAP", timelap, 60)

        cur_time = int(time.time())

        if int(timelap - cur_time) < -1:
            cache.set("TIMELAP", cur_time, 60)
            write_file = True
            print(cur_time)

        if bytes_data:
            if not bmp_header and bytes_data.startswith(b'BMB'):
                cache.set(key, bytes_data, 60)

            if bmp_header:
                try:
                    import os
                    stream = BytesIO(bmp_header + bytes_data)
                    image = Image.open(stream).convert("RGBA")
                    stream.close()

                    filename = f"capture.bmp"
                    # filename = f"{datetime.now().isoformat()}.bmp"
                    # if write_file:
                    image.save(f'{settings.STATIC_DIR}/{filename}')
                    # os.system(f"ffmpeg -f image2 -r 1/5 -i /tmp/testdata/*.bmp -vcodec mpeg4 -y /tmp/videos/record.mp4")
                    # if filename == "29.bmp":
                    #     os.remove(f'/tmp/testdata/*.bmp')
                except:
                    pass

        # TODO bytes houden totdat we alles kunnen wegschrijven naar een bestand ?

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "send_message", "text": text_data, "bytes": bytes_data}
        )

    async def send_message(self, res):
        """ Receive message from room group """
        # Send message to WebSocket
        if res.get('text', None):
            await self.send(text_data=res.get('text', None))

        if res.get('bytes', None):
            await self.send(bytes_data=res.get('bytes', None))
