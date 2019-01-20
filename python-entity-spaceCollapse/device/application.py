# =============================================
# File: GOW
# Author: Benny Saxen
# Date: 2019-01-20
# Description: Bridge Ioant and GOW
#              Publish and action
# =============================================
from ioant.sdk import IOAnt
import logging
import math
import requests
import time
import datetime
logger = logging.getLogger(__name__)

def publish_ioant_message(t_msg):
    # Message syntax:  message_type global local client_id stream_index
    #                    0      1      2         3          4
    # If RunstepperMotorRaw:
    # direction delay_between_steps number_of_step step_size
    #    5              6           7                8
    #--------------------------------------------------------
    t_par = t_msg.split(" ")
    out_msg = ioant.create_message(t_par[0])
    topic = ioant.get_topic_structure()
    topic['top'] = 'live'
    topic['global'] = t_par[1]
    topic['local'] = t_par[2]
    topic['client_id'] = t_par[3]
    topic['stream_index'] = t_par[4]
    if t_par[0] == "RunStepperMotorRaw":
        out_msg.direction = t_par[5]
        out_msg.delay_between_steps = t_par[6]
        out_msg.number_of_step = t_par[7]
        out_msg.step_size = t_par[8]
    ioant.publish(out_msg, topic)

def subscribe_to_topic():
    configuration = ioant.get_configuration()
    topic = ioant.get_topic_structure()
    topic['top'] = 'live'
    #topic['global'] = 'astenas'
    #topic['local'] = 'nytomta'
    #topic['client_id'] = 'nixie2'
    #topic['message_type'] = 8
    #topic['stream_index'] = 0
    #print "Subscribe to: " + str(topic)
    print "Subscribe to all topics: " + str(topic)
    ioant.subscribe(topic)
    return
#===================================================
def publishData( itopic, ipayload, n, iperiod, ihw ):
#===================================================
	url = conf_gs_url
	server = 'gowServer.php'
	data = {}
	# meta data
	data['do']     = 'data'
	data['topic']  = itopic
	data['no']     = n
	data['wrap']   = conf_wrap
	data['ts']     = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	data['period'] = iperiod
	data['url']    = url
	data['hw']     = ihw
	data['hash']   = 'nohash'
	# payload
	data['payload'] = ipayload
	
	values = urllib.urlencode(data)
	req = 'http://' + url + '/' + server + '?' + values
	print req
	try: 
		response = urllib2.urlopen(req)
		the_page = response.read()
		print 'Message to ' + itopic + ': ' + the_page
		evaluateAction(the_page)
	except urllib2.URLError as e:
		print e.reason
#===================================================        
def setup(configuration):
#===================================================
    """ setup function """
    ioant.setup(configuration)
#===================================================
def loop():
#===================================================
    """ Loop function """
    ioant.update_loop()
#===================================================
def on_message(topic, message):
#===================================================
    print "message received - publish to Space Collapse Server"
    print topic['message_type']
    print topic
    msg_type_string = ioant.get_message_type_name(topic['message_type'])
    #print message.value
    #print topic["message_type"]
    ok = 0
    if(topic['message_type'] == 4): # temperature
       unit = "celcius"
       value = message.value
       ok = 1 
    
    if(topic['message_type'] == 8): # electric power
       unit = "watt"
       value = message.value
       ok = 1
    
    if ok == 1:
       payload = '{ "value": "' + str(value) + '", "unit": "' + str(unit) + '"}'
       publishData(topic3, payload , n, conf_period, conf_hw)

def on_connect():
    """ On connect function. Called when connected to broker """
    # There is now a connection
    subscribe_to_topic()
    #ioant.subscribe("live/#")


# =============================================================================
# Above this line are mandatory functions
# =============================================================================
# Mandatory line
ioant = IOAnt(on_connect, on_message)
