import json
import threading


class RedisListener(threading.Thread):
    def __init__(self, redis_instance, pattern, subscriptions):
        threading.Thread.__init__(self)
        self.redis_instance = redis_instance
        self.pubsub = self.redis_instance.pubsub()
        self.pubsub.psubscribe(pattern)
        self.subscriptions = subscriptions

    def _filter(self, message):
        results = []
        for s in self.subscriptions:
            found_filters = 0
            for key, values in s.items():
                if key not in message.keys():
                    break
                # TODO: add all operators
                if values.get("operator", None) and values.get("value", None):
                    if values["operator"] == "==" and values["value"] != message[key]:
                        break
                    elif values["operator"] == "!=" and values["value"] == message[key]:
                        break
                    elif values["operator"] == "<" and values["value"] >= message[key]:
                        break
                found_filters += 1
            if found_filters == len(s):  # all fields match
                results.append(s)

        return results

    def run(self):
        print("[LISTENER] Test if we can subscribe to the generated publications\n")
        for message in self.pubsub.listen():
            if message["channel"] == b"*":
                continue
            if b"stop" == message["channel"] and b"stop" == message["data"]:  # asta trimit ca sa opresc executia
                print("[LISTENER] Stopped listener")
                break
            decoded_message = json.loads(message["data"])
            found = self._filter(decoded_message)
            if found:
                # daca toate fieldurile din publicatie indeplinesc cerintele din macar o subscriptie, ma pot abona la ea
                for f in found:
                    print("The publication {} matches requirements for subscription {}".format(decoded_message, f))
