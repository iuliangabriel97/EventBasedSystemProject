import json
import redis
import threading
from datetime import datetime
from tema.generator import PublicationsGenerator, Publication


def stringify(pg: Publication):
    pub_str = dict()
    for k, v in vars(pg).items():
        if isinstance(v, datetime):
            pub_str[k] = v.strftime("%d.%m.%Y")
        else:
            pub_str[v] = str(v)
    return pub_str


def generate_pubs_stream(pub_nodes: int):
    pid = 0
    node = redis.StrictRedis(host="localhost", port=6379, db=0)
    print("[PUBLISHER] Generating publications stream from {} publisher nodes \n".format(pub_nodes))

    for pn in range(0, pub_nodes):
        pub_gen = PublicationsGenerator(publications_count=5).generate()
        for pg in pub_gen:
            pg = stringify(pg)  # for json
            node.publish(str(pid), json.dumps(pg))
        pid += 1

    node.publish("stop", "stop")  # for terminating the process


class TestListener(threading.Thread):
    def __init__(self, redis_instance, pattern):
        threading.Thread.__init__(self)
        self.redis_instance = redis_instance
        self.pubsub = self.redis_instance.pubsub()
        self.pubsub.psubscribe(pattern)    # pot sa caut canalele dupa un pattern

    def run(self):
        print("[LISTENER] Test if we can subscribe to the generated publications\n")
        for message in self.pubsub.listen():
            if message["channel"] == b"*":
                continue
            if b"stop" == message["channel"] and b"stop" == message["data"]:  # asta trimit ca sa opresc executia
                print("[LISTENER] Stopped listener")
                break
            print("[LISTENER] Publisher node {} published this: {}".format(message["channel"], message["data"]))


if __name__ == "__main__":

    client = TestListener(redis.StrictRedis(), "*")   # pt subscribe la un anumit canal: "1"
    client.start()

    generate_pubs_stream(3)
