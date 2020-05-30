import pika
import uuid
from datetime import datetime
import os
import logging
import logging.config

from tema.generator import PublicationsGenerator
from publication_pb2 import Publication

ROOT_DIRECTORY = os.path.abspath(os.path.join(__file__, os.pardir))
LOGGING_CONFIG_DIR = os.path.join(ROOT_DIRECTORY, 'loggers')

class PublicationSender(object):
    def __init__(self):
        logging.config.fileConfig(os.path.join(LOGGING_CONFIG_DIR, "PublicationSender.conf"))
        self._logger = logging.getLogger("PublicationSender")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange="publications_routing_table", exchange_type="fanout")
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue
        self.generate_publications()
        # self.logger = logging.getLogger()

    def generate_publications(self):

        pub_gen = PublicationsGenerator(publications_count=50).generate()

        for pub in pub_gen:
            publication = Publication()
            publication.car_model = pub.car_model
            publication.production_date = datetime.strftime(pub.production_date, "%d-%m-%Y")
            publication.max_speed = pub.max_speed
            publication.horsepower = pub.horsepower
            publication.color = pub.color
            publication.ts = int(datetime.now().timestamp())
            corr_id = str(uuid.uuid4())
            self.channel.basic_publish(
                exchange="publications_routing_table",
                routing_key="",
                properties=pika.BasicProperties(
                    timestamp=int(datetime.now().timestamp()),
                    reply_to=self.callback_queue, correlation_id=corr_id,
                ),
                body=publication.SerializeToString(),
            )
            print("Sent publication {} with id {}".format(str(pub), corr_id))
            self._logger.info("Sent publication {} with id {}".format(str(pub), corr_id))

        self.connection.close()

open('Logging/pub_start_logger.csv', 'w').close()
ps = PublicationSender()
with open("Logging/pub_start_logger.csv", 'a') as logging_file:
    logging_file.write('\n')

