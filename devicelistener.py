import pika
import logging
import serial
import json
from time import sleep
from threading import Thread

#Set up serial connection as global
ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=None)

def main():
	#Set up the queue details for Rabbit MQ using queue "automation"
	logging.basicConfig()
	credentials = pika.PlainCredentials('cplsyx', 'cplsyx')
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', credentials))

	#Create queues. Update XML and update Web are written to only. update Device is listened to.
	channel = connection.channel()
	channel.queue_declare(queue='updateXML', durable=True)	
	channel.queue_declare(queue='updateDevice', durable=True)	
	#channel.queue_declare(queue='updateWeb', durable=True)
	
	#Start the device listeners as a thread, so we can also have a responder to the queue
	deviceListener = Thread(target=listenOnSerial, args=[channel])
	deviceListener.daemon = True
	deviceListener.start()
	
	#Start the responder for queue updates here as a thread, so it doesn't interfere with the device listener
	queueListener = Thread(target=listenOnQueue, args=[channel])
	queueListener.daemon = True
	queueListener.start()
	
	#Following code stops the main thread from exiting whilst daemons are running
	while 1:
		sleep(1)
	
	connection.close()

#Takes an incoming message from the device (via RF and the serial port). Check it's a valid LLAP message and then sends it on to the updateXML queue. ALL updates should go to this queue, never to the web directly.
def listenOnSerial(channel):
	while 1:
		incomingData = ser.read()
		if(incomingData != "a"):
			continue
	
		incomingData = ser.read(11) #Already read the 'a', so we expect something like PIONLINExx#
		if(not incomingData.startswith("PI")):
			continue
	
		#We now have what we believe to be a valid LLAP message, addressed to the PI.
		#We can send it on to the queues for processing. We'll format it to JSON as a standard.

		outgoingMessage = "{\"sender\":\"device\",\"message\": \"%s\"}" % ("a"+incomingData) 
		channel.basic_publish(exchange='', routing_key='updateXML', body=outgoingMessage)

def listenOnQueue(channel):
	channel.basic_consume(processQueueMessage, queue='updateDevice')
	channel.start_consuming()

def processQueueMessage(ch, method, properties, body):
	messageData = json.loads(body)
	
	#we only care about messages sent from the "web" part of the setup, so ignore device messages in case there are any on the queue (shouldn't be!).
	if(messageData['sender'] == "device"):
		print "Message recieved from web (%s), sending to device." % messageData['message']	
		#ser.write(message)
	ch.basic_ack(delivery_tag = method.delivery_tag)
		

#Start the program running
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print "Exiting via Ctrl+C"