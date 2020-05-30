#!/usr/bin/env python3

import json
import random
import pika
import uuid
import logging
import logging.config
import os

from project.matching import try_match
from datetime import datetime

ROOT_DIRECTORY = os.path.abspath(os.path.join(__file__, os.pardir))
LOGGING_CONFIG_DIR = os.path.join(ROOT_DIRECTORY, 'loggers')


class Broker(object):
    def __init__(self):
        self.counter = 1
        self.time_values = []
        self.broker_id = str(uuid.uuid4())
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        self.channel = self.connection.channel()
        self.subscriptions_channel = self.connection.channel()
        self.publications_channel = self.connection.channel()
        self.queue = None
        self.queue_result = None
        self.unmatched_subscriptions = []
        self.received_publications_table = []
        self.neighbours = dict()
        self.initiate_broker()
        self.get_subscriptions_from_overlay()

    def initiate_broker(self):
        logging.config.fileConfig(os.path.join(LOGGING_CONFIG_DIR, "Broker.conf"))
        self._logger = logging.getLogger("Broker")
        self.channel.exchange_declare(exchange="brokers_routing_table", exchange_type="fanout")
        self.queue_result = self.channel.queue_declare(queue="", exclusive=True)

        self.queue = self.queue_result.method.queue
        brokers_props = pika.BasicProperties(app_id=self.broker_id, reply_to=self.queue)
        self.channel.basic_publish(
            exchange="brokers_routing_table", routing_key="", properties=brokers_props, body="REGISTER"
        )
        print("Registered broker with id {} in the overlay".format(self.broker_id))
        self._logger.info("Registered broker with id {} in the overlay".format(self.broker_id))

        self.channel.exchange_declare(exchange="neighbours_notification", exchange_type="direct")
        result = self.channel.queue_declare(queue="", exclusive=True)
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
        self.subscriptions_channel.queue_bind(
            exchange="subscriptions_routing_table", queue=self.subscriptions_result_queue
        )

    def find_matching_pubs(self, current_subscription):
        found_pubs = try_match(self.received_publications_table, current_subscription)
        return found_pubs

    def subscription_event_callback(self, cn, method, props, body):
        self.get_subscriptions_from_overlay()
        print("Received subscription {} with id {} from subscriber {}".format(body, props.correlation_id, props.app_id))

        if len(self.received_publications_table) > 0:
            matching_pubs = self.find_matching_pubs(body)
            if matching_pubs:
                for pub in matching_pubs:
                    self.subscriptions_channel.basic_publish(
                        exchange="",
                        routing_key=props.reply_to,  # reply to this client's queue
                        properties=props,
                        body=pub,
                    )
            else:
                print("No matching pubs now :(")
                self.unmatched_subscriptions.append({"body": body, "props": props})
        else:
            print("Haven't received any publications yet, waiting....")

    def consume_subs_events(self):
        self.subscriptions_channel.basic_consume(
            queue=self.queue, on_message_callback=self.subscription_event_callback, auto_ack=True
        )
        # if the queue is empty (all events were consumed and we have unmatched subscriptions, try to match them again:
        if self.queue_result.method.message_count == 0 and len(self.unmatched_subscriptions) > 0:
            for us in self.unmatched_subscriptions:
                self.subscription_event_callback(cn=None, method=None, props=us["props"], body=us["body"])


    def get_publications(self):
        self.publications_channel.exchange_declare(exchange="publications_routing_table", exchange_type="fanout")
        publications_result = self.publications_channel.queue_declare(queue="", exclusive=False)
        self.publications_result_queue = publications_result.method.queue
        self.publications_channel.queue_bind(
            exchange="publications_routing_table", queue=self.publications_result_queue
        )

    def publication_event_callback(self, cn, method, props, body):
        print("Received publication {} with id {} and timestamp {}".format(body, props.correlation_id,
                                                                           datetime.fromtimestamp(
                                                                               props.timestamp).strftime(
                                                                               "%d-%m-%Y %H:%M:%S")))
        self.log_to_file(datetime.fromtimestamp(props.timestamp))
        self.received_publications_table.append(body)

    def consume_publ_events(self):
        self.get_publications()
        self.publications_channel.basic_consume(
            queue=self.publications_result_queue, on_message_callback=self.publication_event_callback, auto_ack=True
        )

    def send_stop_notification(self):
        if len(self.unmatched_subscriptions) > 0:
            # send the publications with no matches to a neighbour before closing:
            for us in self.unmatched_subscriptions:
                neighbour = random.choice([i for i in self.neighbours.keys()])
                self.subscriptions_channel.basic_publish(
                    exchange="", routing_key=self.neighbours[neighbour], properties=us["props"], body=us["body"]
                )
        # send the notification to broker overlay:
        self.channel.basic_publish(
            exchange="brokers_routing_table",
            routing_key="",
            properties=pika.BasicProperties(app_id=self.broker_id, reply_to=self.queue),
            body="BYE",
        )

    def log_to_file(self, sub_timestamp):
        with open("Logging/pub_start_logger.csv", 'a') as logging_file:
            pub_time = (datetime.now().timestamp() - sub_timestamp.timestamp()) * 1000
            logging_file.write(str(int(sub_timestamp.timestamp())) + ', ')
        self.counter = self.counter + 1


b = Broker()
try:
    b.consume_subs_events()
    b.consume_publ_events()
    b.subscriptions_channel.start_consuming()
    b.publications_channel.start_consuming()
except KeyboardInterrupt:
    b.send_stop_notification()
    b.channel.stop_consuming()
