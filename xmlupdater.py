import pika
import logging
import json
import time
from threading import Thread
import xml.etree.ElementTree as ET

def main():
	#Set up the queue details for Rabbit MQ using queue "automation"
	logging.basicConfig()
	credentials = pika.PlainCredentials('cplsyx', 'cplsyx')
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', credentials))	
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	channel.queue_declare(queue='updateXML', durable=True)
	
	#Start threads here
	queueListener = Thread(target=listenOnQueue, args=[channel])
	queueListener.daemon = True
	queueListener.start()
	
	#Following code stops the main thread from exiting whilst daemons are running
	while 1:
		time.sleep(1)
	
	connection.close()

def listenOnQueue(channel):
	channel.basic_consume(processQueueMessage, queue='updateXML')
	channel.start_consuming()

def processQueueMessage(ch, method, properties, body):
	messageData = json.loads(body)

	#if(messageData['sender'] == "device"):
	#print "Message recieved from %s (%s)." % (messageData['sender'], messageData['message'])
	messagedetails = decodeLLAPMessage(messageData['message'])
	
	if(messagedetails['status'] == "ON" or messagedetails['status'] == "OFF"):
		updateStatus(messagedetails['id'], messagedetails['status'], messagedetails['switch'])
		
	ch.basic_ack(delivery_tag = method.delivery_tag)

#Update the XML file with the given status for switch and device ID.
def updateStatus(device, status, switch):
	tree = ET.parse('devices.xml')
	root = tree.getroot()
	switch = root.find("./*[@id='"+device+"']/*[@id='"+switch+"']")
	switch.find('status').text = status
	updatestamp = root.find("./*[@id='"+device+"']/lastupdate")
	updatestamp.text = str(int(time.time())) #time.time() is a float, so we cast it to int and then to string to update
	tree.write('devices.xml')
	return

#Extracts the key information from the LLAP message and returns it as a python 'dict' object (i.e. an associative array)
def decodeLLAPMessage(message):
	message = message[3:]
	switch = message[8]
	
	if(message.startswith("STON")):
		id = message[4:6]
		return {'id':id, 'status':'ON', 'switch':switch}

	if(message.startswith("STOFF")):
		id = message[5:7]
		return {'id':id, 'status':'OFF', 'switch':switch}

	if(message.startswith("ONLINE")):
		id = message[6:8]
		return {'id':id, 'status':'ONLINE', 'switch':switch}

#def createDevice():		#if device is broadcast as online but there's nothing in the XML then we need to create it.
#def getStatus():	#return the status on/off of a switch
#def getDetails():	#return the device and switches
#def updateDeviceRoom(): #as described
#def updateSwitchName(): #as described
#def getStatusAll(): #used for complete website end update
#def getDeviceID(): #need this to return all IDs so that we can automatically assign new ones without needing them hardcoded.
			#something like if ID is -- then generate a new one and write it to the device
			#need to understand how the device code will change for this. also how a rebooted device works.
#Any other actions we need?


#Start the program running
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print "Exiting via Ctrl+C"