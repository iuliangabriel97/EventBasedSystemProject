import random
import pika


class BrokerOverlay(object):
    def __init__(self):
        self.last_broker_id = None  # the last broker a subscription was sent to
        self.registered_brokers = dict()
        self.brokers_channel = None
        self.subscriptions_channel = None
        self.subscriptions_result_queue = None
        self.broker_result_queue = None
        self.initiate_overlay()

    def initiate_overlay(self):
        """
        Subscribers connect to the broker overlay randomly and register 10.000 subscriptions -> fanout exchange type
        """
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))

        self.brokers_channel = connection.channel()
        self.brokers_channel.exchange_declare(exchange="brokers_routing_table", exchange_type="fanout")
        brokers_result = self.brokers_channel.queue_declare(queue="", exclusive=True)
        self.broker_result_queue = brokers_result.method.queue
        self.brokers_channel.queue_bind(exchange="brokers_routing_table", queue=self.broker_result_queue)

        self.subscriptions_channel = connection.channel()
        self.subscriptions_channel.exchange_declare(exchange="subscriptions_routing_table", exchange_type="fanout")
        subscriptions_result = self.subscriptions_channel.queue_declare(queue="", exclusive=True)
        self.subscriptions_result_queue = subscriptions_result.method.queue
        self.subscriptions_channel.queue_bind(
            exchange="subscriptions_routing_table", queue=self.subscriptions_result_queue
        )

    def register_brokers(self, ch, method, properties, body):
        broker_id = properties.app_id
        broker_queue_name = properties.reply_to
        if body == b"REGISTER":
            print("Broker with id {} was registered".format(broker_id))
            self.registered_brokers[broker_id] = broker_queue_name

            if len(self.registered_brokers.keys()) > 1:
                channel = pika.BlockingConnection(pika.ConnectionParameters(host="localhost")).channel()
                channel.exchange_declare(exchange="neighbours_notification", exchange_type="direct")
                # notify the other brokers of their neighbours
                channel.basic_publish(
                    exchange="neighbours_notification", routing_key="neighbours", body=str(self.registered_brokers)
                )
        elif body == b"BYE":
            print("Broker with id {} was disconnected".format(broker_id))
            del self.registered_brokers[broker_id]
            if len(self.registered_brokers) > 0:
                channel = pika.BlockingConnection(pika.ConnectionParameters(host="localhost")).channel()
                channel.exchange_declare(exchange="neighbours_notification", exchange_type="direct")
                # notify the other brokers of their neighbours
                channel.basic_publish(
                    exchange="neighbours_notification", routing_key="neighbours", body=str(self.registered_brokers)
                )

    def _send_to_next_broker(self):
        # send the subscriptions to the next broker in the list
        found_current = False
        for b_id, b_q in self.registered_brokers.items():
            if b_id == self.last_broker_id:
                found_current = True
            elif found_current:
                return b_id

        # if the last broker used was the last one to register, send the subs to the first one
        return next(iter(self.registered_brokers))

    def register_subscriptions(self, ch, method, properties, body):
        if len(self.registered_brokers) > 0:
            if not self.last_broker_id:
                # if no subscriptions where sent to any brokers, choose a random one
                self.last_broker_id = random.choice([i for i in self.registered_brokers.keys()])
            else:
                self.last_broker_id = self._send_to_next_broker()
            print("last broker: ", self.last_broker_id)
            self.subscriptions_channel.basic_publish(
                exchange="", routing_key=self.registered_brokers[self.last_broker_id], properties=properties, body=body
            )
            print("Subscription with id {} sent to broker {}".format(properties.correlation_id, self.last_broker_id))

    def consume_network_events(self):
        self.brokers_channel.basic_consume(queue=self.broker_result_queue, on_message_callback=self.register_brokers)
        # self.brokers_channel.start_consuming()

        self.subscriptions_channel.basic_consume(
            queue=self.subscriptions_result_queue, on_message_callback=self.register_subscriptions, auto_ack=True
        )
        self.subscriptions_channel.start_consuming()


BO = BrokerOverlay()
BO.consume_network_events()

