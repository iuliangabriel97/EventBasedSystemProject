import pika


class QueueListener(object):
    def __init__(self, queue):
        self.connection = None
        self.channel = None
        self.queue = queue
        self.get_connection()

    def get_connection(self):
        # establishing the connection and declaring the queue
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)

    @staticmethod
    def on_request(cn, method, props, body):
        # We declare a callback for basic_consume
        # It's executed when the request is received. It does the work and sends the response back.
        print("Received publication {} with id {}".format(body, props.correlation_id))

        cn.basic_publish(
            exchange="",
            routing_key=props.reply_to,
            properties=pika.BasicProperties(content_type="application/json", correlation_id=props.correlation_id),
            body="The publication {} was sent!".format(str(body)),
        )
        cn.basic_ack(delivery_tag=method.delivery_tag)

    def consume(self):
        # We might want to run more than one server process.
        # In order to spread the load equally over multiple servers we need to set the prefetch_count setting
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue, on_message_callback=self.on_request)

        print("Waiting for requests")
        self.channel.start_consuming()


ql = QueueListener("publications")
ql.consume()
