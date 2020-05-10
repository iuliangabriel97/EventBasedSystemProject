#!/usr/bin/env python
import pika
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost' ,port=5672))
channel = connection.channel()

channel.exchange_declare(exchange='testing',
                         exchange_type='headers')

result = channel.queue_declare('client1', exclusive=True)
if not result:
    print('Queue didnt declare properly!')
    sys.exit(1)
queue_name = result.method.queue
print("___{}___".format(queue_name))

channel.queue_bind(exchange='testing',
                   queue=queue_name,
                   routing_key='',
                   arguments={'car_model':'Fiat','x-match': 'any'})


def callback(ch, method, properties, body):
    print("{headers}:{body}".format(headers=properties.headers,
                                    body=body))


channel.basic_consume(queue=queue_name, on_message_callback=callback)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print('Bye')
finally:
    connection.close()
