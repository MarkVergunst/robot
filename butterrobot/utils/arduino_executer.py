
class ArduinoExecutor:
    """
    hier komt de uitsplitsing voor wat de robot allemaal kan doen. (aangeroepen door mobile app via de websocket
     connectie) Executor
    """

    @classmethod
    def connect(cls, context):
        return {
            "message": "connected",
            "event": context.get("event")
        }

    @classmethod
    def ride(cls, context):
        action = context.get('action', None)
        pressed = context.get('pressed', None)

        if action == "forward":
            return {
                "actions": {
                    "left_direction": 1,
                    "right_direction": 1,
                    "pwm": 255 if pressed else 0
                }
            }

        if action == "backward":
            return {
                "actions": {
                    "left_direction": 0,
                    "right_direction": 0,
                    "pwm": 255 if pressed else 0
                }
            }

        if action == "left":
            return {
                "actions": {
                    "left_direction": 0,
                    "right_direction": 1,
                    "pwm": 255 if pressed else 0
                }
            }

        if action == "right":
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