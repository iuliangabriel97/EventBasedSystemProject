import pika
import uuid

from tema.generator import PublicationsGenerator


class PublicationSender(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange="publications_routing_table", exchange_type="fanout")
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue
        self.generate_publications()

    def generate_publications(self):
        pub_gen = PublicationsGenerator(publications_count=5).generate()

        for pg in pub_gen:
            corr_id = str(uuid.uuid4())
            self.channel.basic_publish(
                exchange="publications_routing_table",
                routing_key="",
                properties=pika.BasicProperties(
                    content_type="application/json", reply_to=self.callback_queue, correlation_id=corr_id,
                ),
                body=str(pg),
            )
            print("Sent publication {} with id {}".format(str(pg), corr_id))

        self.connection.close()

ps = PublicationSender()



