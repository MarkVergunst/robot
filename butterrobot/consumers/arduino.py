import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from butterrobot.utils.strategy import ArduinoStrategy


class ArduinoConsumer(AsyncJsonWebsocketConsumer):
    room_group_name = None
    current_user = None

    async def connect(self):
        self.room_group_name = 'room_%s' % self.scope['url_route']['kwargs']['room_code']
        self.current_user = self.scope['user']
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print("Disconnected")
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        """
        Receive message from WebSocket.
        Get the event and send the appropriate event
        """
        response = json.loads(text_data)
        event = response.get("event", None)

        executor = ArduinoStrategy(event)

        result = executor.run(response)

        if response.get('id'):
            result.update({"id": response.get('id')})

        if not result.get('type'):
            result['type'] = 'send_message'

        if not result.get('event'):
            result['event'] = event

        if not result.get('message'):
            result['message'] = response.get('message', '')

        await self.channel_layer.group_send(self.room_group_name, result)

    async def send_message(self, res):
        """ Receive message from room group """
        # Send message to WebSocket
        res.pop('type')
        if res.get('bytes', None):
            await self.send(bytes_data=res.get('bytes', None))
        else:
            await self.send(json.dumps(res))
