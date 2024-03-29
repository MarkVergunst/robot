from butterrobot.utils.arduino_executer import ArduinoExecutor


class ArduinoStrategy:
    def __init__(self, func=None):
        self.name = 'Geen method gevonden'
        if func is not None:
            try:
                self.run = getattr(ArduinoExecutor, func)
            except Exception as exc:
                self.name = f"{self.name} voor {func}"
                print(exc)

    def run(self, context):
        print(self.name)

        return {
            "message": "empty",
            "event": "empty"
        }
