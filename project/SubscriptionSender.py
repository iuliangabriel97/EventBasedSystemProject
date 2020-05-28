import pika
import uuid

from tema.generator import SubscriptionsGenerator


class SubscriptionSender(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange="subscriptions_routing_table", exchange_type="fanout")
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue
        self.generate_subscriptions()

    def on_response(self, ch, method, props, body):
        print("received matching publication")

    def generate_subscriptions(self):
        sub_gen = SubscriptionsGenerator(subscriptions_count=1).generate()
        for sg in sub_gen:
            corr_id = str(uuid.uuid4())
            self.channel.basic_publish(
                exchange="subscriptions_routing_table",
                routing_key="",
                properties=pika.BasicProperties(
                    content_type="application/json", reply_to=self.callback_queue, correlation_id=corr_id,
                ),
                body=str(sg),
            )
            print("Sent subscription with id {}".format(corr_id))

        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)

    def consume_event(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.start_consuming()


ps = SubscriptionSender()
try:
    ps.consume_event()
except:
    ps.channel.stop_consuming()
