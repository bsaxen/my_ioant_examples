# =============================================
# Benny Saxen
# Date: 2017-09-23
# Description: API.ai webhook with IOAnt support
# =============================================

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

import json
import os
import thread
import server

from ioant.sdk import IOAnt
import logging
import hashlib
logger = logging.getLogger(__name__)

tValue = []
aliasToHash = []
aliasToTopic = []

#----------------------------------------------------
def getFilenameFromTopic(topic,extension):
#----------------------------------------------------
    filename = topic['global'] + "_" + topic['local'] + "_" + topic['client_id'] + "_" + topic['stream_index']
    filename = filename + "." + extension
    return filename

#----------------------------------------------------
def getFilenameFromAlias(alias,extension):
#----------------------------------------------------
    filename = alias + "." + extension
    return filename

#----------------------------------------------------
def writeSubscription(topic,alias):
#----------------------------------------------------
    filename = getFilenameFromTopic(topic,"sub")
    file = open(filename,"w")
    file.write(alias)
    file.close()

    #filename = getFilenameFromAlias(alias,"sub")
    #file = open(filename,"w")
    #file.write(topic)
    #file.close()
    return

#----------------------------------------------------
def readAlias(topic):
#----------------------------------------------------
    filename = getFilenameFromTopic(topic,"sub")
    file = open(filename,"r")
    line = file.read()
    file.close()
    return alias

#----------------------------------------------------
def writeValue(alias,value):
#----------------------------------------------------
    filename = getFilenameFromAlias(alias,"value")
    file = open(filename,"w")
    file.write(value)
    file.close()
    return

#----------------------------------------------------
def readValue(alias):
#----------------------------------------------------
    filename = getFilenameFromAlias(alias,"value")
    file = open(filename,"r")
    value = file.read()
    file.close()
    return value

#----------------------------------------------------
def getTopicHash(topic):
#----------------------------------------------------
    res = topic['top'] + topic['global'] + topic['local'] + topic['client_id'] + str(topic['message_type']) + str(topic['stream_index'])
    tres = hash(res)
    tres = tres% 10**8
    return tres

#----------------------------------------------------
def subscribe_to_topic(t_alias,t_global,t_local,t_clientid, t_streamindex):
#----------------------------------------------------
    topic = ioant.get_topic_structure()
    topic['top'] = 'live'
    topic['global'] = t_global
    topic['local'] = t_local
    topic['client_id'] = t_clientid
    #topic['message_type'] = ioant.get_message_type(msgt)
    topic['stream_index'] = str(t_streamindex)

    writeSubscription(topic,t_alias)

    print("Subscribe to: ", str(topic))
    ioant.subscribe(topic)
    return

#----------------------------------------------------
def intent_request(req):
#----------------------------------------------------
    global tValue
    global aliasToHash
    global aliasToTopic

    """ Handles and responds on webhook request from API.ai """
    action = req.get("result").get("action")
    print("request ioant action:", action)

    topic = ioant.get_topic_structure()
    #topic['global'] = configuration["api"]["ai"]["global"]
    #topic['local'] =  configuration["publish_topic"]["CPUtemp"]["local"]
    topic['client_id'] =  "bot1"
    #topic['stream_index'] =  configuration["publish_topic"]["CPUtemp"]["stream_index"]

#----------------------------------------------------
    if action == "heater.increase":
#----------------------------------------------------
        steps = int(req.get("result").get("parameters").get("steps"))
        if steps < 1:
            steps = 1
        if steps > 20:
            steps = 20
        topic['global'] = "kil"
        topic['local'] =  "kvv32"
        topic['client_id'] =  "D1"
        msg = ioant.create_message("RunStepperMotorRaw")
        msg.direction = msg.COUNTER_CLOCKWISE
        msg.delay_between_steps = 5
        msg.number_of_step = steps
        msg.step_size = msg.FULL_STEP
        action_text = "Warmer " + str(msg.number_of_step)
        ioant.publish(msg,topic)
#----------------------------------------------------
    elif action == "heater.decrease":
#----------------------------------------------------
        steps = int(req.get("result").get("parameters").get("steps"))
        if steps < 1:
            steps = 1
        if steps > 20:
            steps = 20
        topic['global'] = "kil"
        topic['local'] =  "kvv32"
        topic['client_id'] =  "D1"
        msg = ioant.create_message("RunStepperMotorRaw")
        msg.direction = msg.CLOCKWISE
        msg.delay_between_steps = 5
        msg.number_of_step = steps
        msg.step_size = msg.FULL_STEP
        action_text = "Cooler " + str(msg.number_of_step)
        ioant.publish(msg,topic)
#----------------------------------------------------
    elif action == "mqtt.subscribe":
#----------------------------------------------------
        t_alias = str(req.get("result").get("parameters").get("alias"))
        topic['global'] = str(req.get("result").get("parameters").get("global"))
        topic['local'] = str(req.get("result").get("parameters").get("local"))
        topic['client_id'] = str(req.get("result").get("parameters").get("clientid"))
        topic['stream_index'] = str(req.get("result").get("parameters").get("streamindex"))
        #aliasToHash[topic['alias']] = getTopicHash(topic)
        subscribe_to_topic(t_alias,topic['global'],topic['local'],topic['client_id'],topic['stream_index'])
        action_text = "Subscribe to  " + str(topic) + " " + t_alias
#----------------------------------------------------
    elif action == "show.value":
#----------------------------------------------------
        topic_alias = str(req.get("result").get("parameters").get("alias"))
        value = tValue[aliasToHash[topic_alias]]
        action_text = "Value is " + str(value)
    else:
        return {}

    print("Action chosen:" + action_text)

    # Dict that will be returned as JSON to API.ai
    return {
        "speech": action_text,
        "displayText": action_text,
        # "data": data,
        # "contextOut": [],
        "source": ioant.get_configuration()["app_name"]
    }

#=====================================================
def setup(configuration):
#=====================================================
    """ setup function """
    ioant.setup(configuration)
    thread.start_new_thread(server.init_server,(configuration["web_server"]["port"],
                                                intent_request))
    print("Setup Done")

#=====================================================
def loop():
#=====================================================
    global tValue
    #global hashToAlias
    global aliasToHash
    global aliasToTopic
    """ Loop function """
    ioant.update_loop()

#=====================================================
def on_message(topic, message):
#=====================================================
    #global tValue
    #tHash = getTopicHash(topic)
    print("Message recieved ...", ioant.get_message_type_name(topic['message_type']))
    #if topic["message_type"] == ioant.get_message_type("Trigger"):
    t_alias = readAlias(topic)
    if "Temperature" == ioant.get_message_type_name(topic['message_type']):
        print("Message received of type Temperature")
        print("Contains value:" + str(message.value))
        writeValue(t_alias,str(message.value))
    if "ElectricPower" == ioant.get_message_type_name(topic['message_type']):
        print("Message received of type ElectricPower")
        print("Contains value:" + str(message.value))
        writeValue(t_alias,str(message.value))

#=====================================================
def on_connect():
#=====================================================
    """ On connect function. Called when connected to broker """


ioant = IOAnt(on_connect, on_message)
