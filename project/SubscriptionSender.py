import pika
import uuid
from datetime import datetime
import os

from tema.generator import SubscriptionsGenerator
from subscription_pb2 import Subscription
import logging
import logging.config

ROOT_DIRECTORY = os.path.abspath(os.path.join(__file__, os.pardir))
LOGGING_CONFIG_DIR = os.path.join(ROOT_DIRECTORY, 'loggers')

class SubscriptionSender(object):
    def __init__(self):
        logging.config.fileConfig(os.path.join(LOGGING_CONFIG_DIR, "SubscriptionSender.conf"))
        self._logger = logging.getLogger("SubscriptionSender")
        self._id = str(uuid.uuid4())
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange="subscriptions_routing_table", exchange_type="fanout")
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue
        self.generate_subscriptions()


    def on_response(self, ch, method, props, body):
        pub = Subscription()
        # pub.Parse
        print("Got this matching pub: {} for {} with timestamp {}".format(body, props.correlation_id, datetime.fromtimestamp(props.timestamp).strftime("%d-%m-%Y %H:%M:%S")))
        self._logger.info("Got this matching pub: {} for {}".format(body, props.correlation_id))
        with open("Logging/pub_recv_logger.csv", 'a') as logging_file:
            logging_file.write(str(props.timestamp)+', ')

    def generate_subscriptions(self):
        sub_gen = SubscriptionsGenerator(subscriptions_count=10).generate()

        for sub in sub_gen:
            subscription = Subscription()
            for key, value in sub.items():
                if key == "car_model":
                    subscription.car_model.operator = value["operator"]
                    subscription.car_model.value = value["value"]
                elif key == "horsepower":
                    subscription.horsepower.operator = value["operator"]
                    subscription.horsepower.value = value["value"]
                elif key == "production_date":
                    subscription.production_date.operator = value["operator"]
                    subscription.production_date.value = value["value"]
                elif key == "color":
                    subscription.color.operator = value["operator"]
                    subscription.color.value = value["value"]
                elif key == "max_speed":
                    subscription.max_speed.operator = value["operator"]
                    subscription.max_speed.value = value["value"]
            corr_id = str(uuid.uuid4())
            self.channel.basic_publish(
                exchange="subscriptions_routing_table",
                routing_key="",
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=corr_id,
                    app_id=self._id,
                    timestamp=int(datetime.now().timestamp()),
                ),
                body=subscription.SerializeToString(),
            )
            print("Sent subscription {} with id {}".format(subscription, corr_id))
            self._logger.info("Sent subscription with id {}".format(corr_id))

    def consume_event(self):
        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.start_consuming()

open('Logging/pub_recv_logger.csv', 'w').close()
ps = SubscriptionSender()
try:
    ps.consume_event()
except:
    ps.channel.stop_consuming()
