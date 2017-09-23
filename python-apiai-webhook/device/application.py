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

currentRed = 1;
currentGreen = 1;
currentBlue = 1;
pwm_max = 1023;

from ioant.sdk import IOAnt
import logging
import hashlib
logger = logging.getLogger(__name__)

def subscribe_to_topic(t_global,t_local,t_clientid):
    topic = ioant.get_topic_structure()
    topic['top'] = 'live'
    topic['global'] = t_global
    topic['local'] = t_local
    topic['client_id'] = t_clientid
    #topic['message_type'] = ioant.get_message_type(msgt)
    #topic['stream_index'] = configuration["subscribe_topic"][par]["stream_index"]
    print "Subscribe to: " + str(topic)
    ioant.subscribe(topic)
    return

def intent_request(req):
    global currentRed
    global currentGreen
    global currentBlue

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
        topic_global = int(req.get("result").get("parameters").get("global"))
        topic_local = int(req.get("result").get("parameters").get("local"))
        topic_clientid = int(req.get("result").get("parameters").get("clientid"))
        subscribe_to_topic(topic_global,topic_local,topic_clientid)
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


def setup(configuration):
    """ setup function """
    ioant.setup(configuration)
    thread.start_new_thread(server.init_server,(configuration["web_server"]["port"],
                                                intent_request))
    print("Setup Done")

def loop():
    """ Loop function """
    ioant.update_loop()


def on_message(topic, message):
    if "Temperature" == ioant.get_message_type_name(topic[message_type]):
        logger.debug("Message received of type temperature")
        logger.debug("Contains value:" + str(message.value))


def on_connect():
    """ On connect function. Called when connected to broker """


ioant = IOAnt(on_connect, on_message)
