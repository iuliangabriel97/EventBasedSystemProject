from datetime import datetime

import pika
import uuid

from tema.generator import PublicationsGenerator


class PublicationSender(object):
    def __init__(self):
        # We establish a connection, channel and declare an exclusive 'callback' queue for replies
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue
        # We subscribe to the 'callback' queue, so that we can receive RPC responses.
        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)

    def on_response(self, ch, method, props, body):
        """
        Executed on every response, for every message it
        checks if the publication id is the one we're looking for. If so, it saves the response in self.response and
        breaks the consuming loop.
        """
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, publication):
        # the actual RPC request
        self.response = None
        #  we generate a unique correlation_id number and save it - the 'on_response' callback function will
        #  use this value to catch the appropriate response
        self.corr_id = str(uuid.uuid4())
        # publish the request message, with two properties: reply_to and correlation_id
        self.channel.basic_publish(
            exchange="",
            routing_key="publications",
            properties=pika.BasicProperties(
                content_type="application/json", reply_to=self.callback_queue, correlation_id=self.corr_id,
            ),
            body=str(publication),
        )
        # wait until the proper response arrives
        while self.response is None:
            self.connection.process_data_events()
        # return the response back to the user
        # return self.response

        print(self.response)


pub_gen = PublicationsGenerator(publications_count=5).generate()
ps = PublicationSender()

for pg in pub_gen:
    ps.call(pg)
