import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='automation')

channel.basic_publish(exchange='',
                      routing_key='automation',
                      body='Hello World!')
print " [x] Sent 'Hello World!'"
connection.close()