import xml.etree.ElementTree as ET
import time
tree = ET.parse('devices.xml')
root = tree.getroot()

#for device in root:
#	if (device.attrib['id'] == "BR"):
#		results = device.findall('switch')
#		for switch in results:
#			if(switch.attrib['id'] == "1"):
#				switch.find('name').text = "Buttcheeks"
#				print switch.find('name').text
#tree.write('devices.xml')
device = "BR"
switchid = "1"
updatetime = root.find("./*[@id='"+device+"']/lastupdate")
switch = root.find("./*[@id='"+device+"']/*[@id='"+switchid+"']")

print updatetime.text
print switch.find('name').text
print switch.find('status').text
updatetime.text = int(time.time())
print updatetime.text