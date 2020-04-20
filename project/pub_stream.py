import json
import redis
from datetime import datetime

from project.listener import RedisListener
from tema.generator import PublicationsGenerator, Publication, SubscriptionsGenerator


def stringify(pg: Publication):
    pub_str = dict()
    for k, v in vars(pg).items():
        if isinstance(v, datetime):
            pub_str[k] = v.strftime("%d.%m.%Y")
        else:
            pub_str[k] = str(v)
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


if __name__ == "__main__":
    # TODO: use generated subscriptions
    # s1 = SubscriptionsGenerator(subscriptions_count=3)
    # client = RedisListener(redis.StrictRedis(), "*", s1.generate())
    subscriptions = [
        {"car_model": {"operator": "==", "value": "Fiat"}},
        {"car_model": {"operator": "==", "value": "Mercedes"}, "horsepower": {"operator": "<", "value": "100"}},
        {"car_model": {"operator": "==", "value": "Opel"}, "color": {"operator": "==", "value": "green"}},
    ]
    client = RedisListener(redis.StrictRedis(), "*", subscriptions)
    client.start()

    generate_pubs_stream(3)
