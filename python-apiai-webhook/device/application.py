# =============================================
# Benny Saxen
# Date: 2017-09-17
# Description: API.ai webhook example with IOAnt support
# =============================================

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

import json
import os
import thread
import server

currentRed = 0;
currentGreen = 0;
currentBlue = 0;

from ioant.sdk import IOAnt
import logging
import hashlib
logger = logging.getLogger(__name__)

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


    if action == "rgb.set":
        color = req.get("result").get("parameters").get("color")
        pwm = int(req.get("result").get("parameters").get("pwm"))
        if pwm > 255:
            pwm = 255;
        if pwm < 0:
            pwm = 0;
        action_text = "rgb set"
        msg = ioant.create_message("Color")
        if color == "red":
            msg.red = pwm
            currentRed = pwm
        if color == "green":
            msg.green = pwm
            currentGreen = pwm
        if color == "blue":
            msg.blue = pwm
            currentBlue = pwm
        ioant.publish(msg,topic)
    elif action == "rgb.increase":
        color = req.get("result").get("parameters").get("color")
        pwm = int(req.get("result").get("parameters").get("pwm"))
        action_text = "rgb increase"
        msg = ioant.create_message("Color")
        if color == "red":
            itemp = currentRed + pwm
            if itemp > 255:
                itemp = 255;
            if itemp < 0:
                itemp = 0;
            currentRed = itemp
            msg.red = itemp
        if color == "green":
            itemp = currentGreen + pwm
            if itemp > 255:
                itemp = 255;
            if itemp < 0:
                itemp = 0;
            currentGreen = itemp
            msg.green = itemp
        if color == "blue":
            itemp = currentBlue + pwm
            if itemp > 255:
                itemp = 255;
            if itemp < 0:
                itemp = 0;
            currentBlue = itemp
            msg.blue = itemp
        ioant.publish(msg,topic)
    elif action == "rgb.decrease":
        color = req.get("result").get("parameters").get("color")
        pwm = int(req.get("result").get("parameters").get("pwm"))
        action_text = "rgb decrease"
        msg = ioant.create_message("Color")
        if color == "red":
            itemp = currentRed - pwm
            if itemp > 255:
                itemp = 255;
            if itemp < 0:
                itemp = 0;
            currentRed = itemp
            msg.red = itemp
        if color == "green":
            itemp = currentGreen - pwm
            if itemp > 255:
                itemp = 255;
            if itemp < 0:
                itemp = 0;
            currentGreen = itemp
            msg.green = itemp
        if color == "blue":
            itemp = currentBlue - pwm
            if itemp > 255:
                itemp = 255;
            if itemp < 0:
                itemp = 0;
            currentBlue = itemp
            msg.blue = itemp
        ioant.publish(msg,topic)
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
