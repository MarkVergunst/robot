
class ArduinoExecuter:
    """
    hier komt de uitsplitsing voor wat de robot allemaal kan doen. (aangeroepen door mobile app via de websocket
     connectie)
    """

    @classmethod
    def connect(cls, context):
        return {
            "message": "connected",
            "event": context.get("event")
        }

    @classmethod
    def bend(cls, context):
        # TODO
        return {
            "actions": {}
        }

    @classmethod
    def camera(cls, context):

        ipaddr = context.get('camera', None)

        return {
            "camera": f"<iframe width='100%' height='100%' src='http://{ipaddr}' frameborder='0' allow='autoplay; encrypted-media' allowfullscreen></iframe>",
            "ip": ipaddr
        }

    @classmethod
    def ride(cls, context):
        action = context.get('action', None)
        pressed = context.get('pressed', None)

        if action == "forward":
            print("rij vooruit")
            return {
                "actions": {
                    "left_direction": 1,
                    "right_direction": 1,
                    "pwm": 255 if pressed else 0
                }
            }

        if action == "backward":
            print("rij achteruit")
            return {
                "actions": {
                    "left_direction": 0,
                    "right_direction": 0,
                    "pwm": 255 if pressed else 0
                }
            }

        if action == "left":
            print("rij links")
            return {
                "actions": {
                    "left_direction": 0,
                    "right_direction": 1,
                    "pwm": 255 if pressed else 0
                }
            }

        if action == "right":
            print("rij right")
            return {
                "actions": {
                    "left_direction": 1,
                    "right_direction": 0,
                    "pwm": 255 if pressed else 0
                }
            }

        return {
            "actions": {}
        }

    @classmethod
    def send_frame(cls, context):
        print("send_frame")
        print(context)

        # TODO logica om naar rechts te rijden

        return {
            "message": "We gaan naar rechts",
            "event": context.get("event")
        }
