import boto3
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.core.cache import cache
from PIL import Image
from io import BytesIO

if settings.USE_S3:
    s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)


class ImageConsumer(AsyncJsonWebsocketConsumer):
    room_group_name = None
    current_user = None

    async def connect(self):
        self.room_group_name = 'room_camera_%s' % self.scope['url_route']['kwargs']['room_code']
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
        # print("starting receiving message")
        key = f"BMP_HEADER"
        from PIL import ImageFile
        ImageFile.LOAD_TRUNCATED_IMAGES = True

        bmp_header = cache.get(key)
        if bytes_data:
            if not bmp_header and bytes_data.startswith(b'BMB'):
                cache.set(key, bytes_data, 30)

            if bmp_header:
                try:
                    save_img = True
                    stream = BytesIO(bmp_header + bytes_data)

                    image = Image.open(stream).convert("RGBA").rotate(180)

                    if sum(image.convert("L").getextrema()) in (0, 2):
                        # either all black or all white
                        save_img = False

                    stream.close()

                    filename = f"capture.bmp"
                    if save_img:
                        if settings.USE_S3:

                            in_mem_file = BytesIO()

                            # format here would be something like "JPEG". See below link for more info.
                            image.save(in_mem_file, format="bmp")
                            bucket.put_object(Key='media/capture.bmp', Body=in_mem_file.getvalue(), ACL='public-read')

                            in_mem_file.close()

                        else:
                            image.save(f'{settings.STATIC_ROOT}/../static/{filename}')

                except Exception as exc:
                    print(exc)

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
