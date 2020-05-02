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
        self.initiate_broker()
        self.get_subscriptions_from_overlay()

    def initiate_broker(self):

        self.channel.exchange_declare(exchange="brokers_routing_table", exchange_type="fanout")
        result = self.channel.queue_declare(queue="", exclusive=True)

        self.queue = result.method.queue
        brokers_props = pika.BasicProperties(app_id=self.broker_id, reply_to=self.queue)
        self.channel.basic_publish(
            exchange="brokers_routing_table", routing_key="", properties=brokers_props, body="broker"
        )
        print("Registered broker with id {} in the overlay".format(self.broker_id))

    def get_subscriptions_from_overlay(self):
        self.subscriptions_channel.exchange_declare(exchange="subscriptions_routing_table", exchange_type="fanout")
        subscriptions_result = self.subscriptions_channel.queue_declare(queue="", exclusive=True)
        self.subscriptions_result_queue = subscriptions_result.method.queue
        self.subscriptions_channel.queue_bind(exchange="subscriptions_routing_table", queue=self.subscriptions_result_queue)

    def subscription_event_callback(self, cn, method, props, body):
        self.get_subscriptions_from_overlay()
        self.received_subscriptions_table.append(body)
        print("Received subscription {} with id {}".format(body, props.correlation_id))

    def consume_subs_events(self):
        self.subscriptions_channel.basic_qos(prefetch_count=1)
        self.subscriptions_channel.basic_consume(queue=self.queue, on_message_callback=self.subscription_event_callback, auto_ack=True)
        self.subscriptions_channel.start_consuming()

    def get_publications(self):
        self.publications_channel.exchange_declare(exchange="publications_routing_table", exchange_type="fanout")
        publications_result = self.publications_channel.queue_declare(queue="", exclusive=True)
        self.publications_result_queue = publications_result.method.queue
        self.publications_channel.queue_bind(exchange="publications_routing_table", queue=self.publications_result_queue)

    def publication_event_callback(self, cn, method, props, body):
        # le trimit pe toate unui singur subscriber:
        self.received_publications_table.append(body)
        print("Received publication {} with id {}".format(body, props.correlation_id))

    def consume_publ_events(self):
        self.get_publications()
        self.publications_channel.basic_qos(prefetch_count=1)
        self.publications_channel.basic_consume(queue=self.publications_result_queue, on_message_callback=self.publication_event_callback, auto_ack=True)
        self.publications_channel.start_consuming()


b = Broker()
try:
    b.consume_publ_events()
    b.consume_subs_events()
except KeyboardInterrupt:
    b.channel.stop_consuming()
