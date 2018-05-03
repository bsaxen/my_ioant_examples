# =============================================
# File: spacecollapse
# Author: Benny Saxen
# Date: 2018-05-03
# Description: Bridge Ioant and Spacecollapse
#              Publish and action
# =============================================
from ioant.sdk import IOAnt
import logging
import math
import requests
import time
import datetime
logger = logging.getLogger(__name__)

def publish_ioant_message(t_msg,t_global,t_local_t_client_id,t_stream_index):
    out_msg = ioant.create_message(t_msg)
    topic = ioant.get_topic_structure()
    topic['top'] = 'live'
    topic['global'] = t_global
    topic['local'] = t_local
    topic['client_id'] = t_client_id
    topic['stream_index'] = t_stream_index
    if t_msg == "RunStepperMotorRaw":
        out_msg.direction = direction
        out_msg.delay_between_steps = 5
        out_msg.number_of_step = steps
        out_msg.step_size = out_msg.StepSize.Value("FULL_STEP")
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

def setup(configuration):
    """ setup function """
    ioant.setup(configuration)

def loop():
    """ Loop function """
    ioant.update_loop()

def on_message(topic, message):
    print "message received - publish to Space Collapse Server"
    print topic['message_type']
    print topic
    msg_type_string = ioant.get_message_type_name(topic['message_type'])
    #print message.value
    #print topic["message_type"]
    if(topic['message_type'] == 4): # temperature
       unit = "celcius"
    if(topic['message_type'] == 8): # electric power
       unit = "watt"
    scUrl = "http://spacecollapse.simuino.com/scServer.php?"
    scUrl = scUrl + "type=" + msg_type_string
    scUrl = scUrl + "&label=" + topic["global"]+'_'+topic["local"]+'_'+topic["client_id"]+'_'+str(topic["stream_index"])
    scUrl = scUrl + "&value=" + "{0:.2f}".format(message.value)
    scUrl = scUrl + "&unit=" + unit
    scUrl = scUrl + "&datetime=" + datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")
    #scUrl = scUrl + "&description=" +
    #%22This%20is%20a%20measurement%20in%20my%20house%22"
    print scUrl
    r = requests.get(scUrl)
    print r.text
    print r.content


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
