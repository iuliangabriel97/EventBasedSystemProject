import pika
from tema.generator import *
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost', port=5672))
channel = connection.channel()

channel.exchange_declare(exchange='testing',
                         exchange_type='headers')

fields = {}
pub_gen = PublicationsGenerator(publications_count=10).generate()

try:
    for pg in pub_gen:
        data = str(pg)
        fields = json.loads(data)
        channel.basic_publish(exchange='testing',
                              routing_key='',
                              body=data,
                              properties= \
                                  pika.BasicProperties(headers=fields))
        print(' [x] Send {0} with headers: {1}'.format(data, fields))
except KeyboardInterrupt:
    print('Bye')
finally:
    connection.close()
