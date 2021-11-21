import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from butterrobot.utils.strategy import ArduinoStrategy


class ArduinoConsumer(AsyncJsonWebsocketConsumer):
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
        print(text_data)
        response = json.loads(text_data)
        event = response.get("event", None)

        if "camera" in response.keys():
            executer = ArduinoStrategy("camera")
        else:
            executer = ArduinoStrategy(event)

        result = executer.run(response)

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
        await self.send(text_data=json.dumps(res))
        #
        # await self.send(text_data=json.dumps({
        #     "payload": res,
        # }))
