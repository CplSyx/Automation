import pika
import xmlupdater

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='automation')

print ' [*] Waiting for messages. To exit press CTRL+C'

def callback(ch, method, properties, body):
    xmlupdater.process(body)

channel.basic_consume(callback,
                      queue='automation',
                      no_ack=True)

channel.start_consuming()