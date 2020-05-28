import json
import pika
import uuid


class Broker(object):
    def __init__(self):
        self.broker_id = str(uuid.uuid4())
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        self.channel = self.connection.channel()
        self.subscriptions_channel = self.connection.channel()
        self.publications_channel = self.connection.channel()
        self.queue = None
        self.received_subscriptions_table = []
        self.received_publications_table = []
        self.neighbours = dict()
        self.initiate_broker()
        self.get_subscriptions_from_overlay()

    def initiate_broker(self):

        self.channel.exchange_declare(exchange="brokers_routing_table", exchange_type="fanout")
        result = self.channel.queue_declare(queue="", exclusive=False)

        self.queue = result.method.queue
        brokers_props = pika.BasicProperties(app_id=self.broker_id, reply_to=self.queue)
        self.channel.basic_publish(
            exchange="brokers_routing_table", routing_key="", properties=brokers_props, body="REGISTER"
        )
        print("Registered broker with id {} in the overlay".format(self.broker_id))

        self.channel.exchange_declare(exchange="neighbours_notification", exchange_type="direct")
        result = self.channel.queue_declare(queue='', exclusive=True)
        neighbours_queue = result.method.queue
        self.channel.queue_bind(exchange="neighbours_notification", queue=neighbours_queue, routing_key="neighbours")
        self.channel.basic_consume(queue=neighbours_queue, on_message_callback=self.update_neighbours, auto_ack=True)

    def update_neighbours(self, cn, method, props, body):
        all_active_brokers = json.loads(body.decode("utf-8").replace("'", '"'))
        if len(all_active_brokers) > len(self.neighbours):
            # a new broker was added!!
            for broker_id, broker_queue in all_active_brokers.items():
                if broker_id != self.broker_id and broker_id not in self.neighbours.keys():
                    self.neighbours.update({broker_id: broker_queue})
        else:
            # a neighbour disconnected!!!
            for neigh_id, neigh_queue in self.neighbours.items():
                if neigh_id != self.broker_id and neigh_id not in all_active_brokers.keys():
                    del self.neighbours[neigh_id]
                    break

        print("My neighbours are: {}".format(self.neighbours))

    def get_subscriptions_from_overlay(self):
        self.subscriptions_channel.exchange_declare(exchange="subscriptions_routing_table", exchange_type="fanout")
        subscriptions_result = self.subscriptions_channel.queue_declare(queue="", exclusive=False)
        self.subscriptions_result_queue = subscriptions_result.method.queue
        self.subscriptions_channel.queue_bind(exchange="subscriptions_routing_table", queue=self.subscriptions_result_queue)

    def subscription_event_callback(self, cn, method, props, body):
        self.get_subscriptions_from_overlay()
        self.received_subscriptions_table.append(body)
        print("Received subscription {} with id {}".format(body, props.correlation_id))

    def consume_subs_events(self):
        self.subscriptions_channel.basic_consume(queue=self.subscriptions_result_queue, on_message_callback=self.subscription_event_callback, auto_ack=True)
        # self.subscriptions_channel.start_consuming()

    def get_publications(self):
        self.publications_channel.exchange_declare(exchange="publications_routing_table", exchange_type="fanout")
        publications_result = self.publications_channel.queue_declare(queue="", exclusive=False)
        self.publications_result_queue = publications_result.method.queue
        self.publications_channel.queue_bind(exchange="publications_routing_table", queue=self.publications_result_queue)

    def publication_event_callback(self, cn, method, props, body):
        # le trimit pe toate unui singur subscriber:
        self.received_publications_table.append(body)
        print("Received publication {} with id {}".format(body, props.correlation_id))

    def consume_publ_events(self):
        self.get_publications()
        self.publications_channel.basic_consume(queue=self.publications_result_queue, on_message_callback=self.publication_event_callback, auto_ack=True)
        # self.publications_channel.start_consuming()

    def send_stop_notification(self):
        self.channel.basic_publish(
            exchange="brokers_routing_table", routing_key="", properties=pika.BasicProperties(app_id=self.broker_id, reply_to=self.queue), body="BYE"
        )


b = Broker()
try:
    b.consume_subs_events()
    b.consume_publ_events()
    b.subscriptions_channel.start_consuming()
    b.publications_channel.start_consuming()
except KeyboardInterrupt:
    b.send_stop_notification()
    b.channel.stop_consuming()
