import json
import threading
import operator

STOP_MESSAGE = "stop"


class RedisListener(threading.Thread):
    def __init__(self, redis_instance, pattern, subscriptions):
        threading.Thread.__init__(self)
        self.redis_instance = redis_instance
        self.pubsub = self.redis_instance.pubsub()
        self.pubsub.psubscribe(pattern)
        self.subscriptions = subscriptions

    @staticmethod
    def check_operator(op, operand1, operand2):
        ops = {'>': operator.gt,
               '<': operator.lt,
               '>=': operator.ge,
               '<=': operator.le,
               '==': operator.eq,
               '!=': operator.ne}
        return ops[op](operand1, operand2)

    def _filter(self, message):
        results = []
        for sub in self.subscriptions:
            found_filters = 0
            for field_name, field_values in sub.items():
                if field_name not in message.keys():
                    break

                if not field_values.get("operator") or not field_values.get("value"):
                    break

                if not RedisListener.check_operator(field_values["operator"], field_values["value"],
                                                    message[field_name]):
                    break

                found_filters += 1
            if found_filters == len(sub):  # all fields match
                results.append(sub)

        return results

    def run(self):
        print("[LISTENER] Test if we can subscribe to the generated publications\n")
        for message in self.pubsub.listen():
            message_channel = message["channel"].decode()
            message_data = message["data"].decode()

            if message_channel == message_data == STOP_MESSAGE:  # asta trimit ca sa opresc executia
                print("[LISTENER] Stopped listener")
                return

            if message_channel == "*":
                continue

            decoded_message = json.loads(message_data)
            found = self._filter(decoded_message)
            if not found:
                continue

            for f in found:
                print("The publication {} matches requirements for subscription {}".format(decoded_message, f))
