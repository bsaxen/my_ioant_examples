# =============================================
# Benny Saxen
# Date: 2017-09-22
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
        steps = req.get("result").get("parameters").get("steps")
        if steps < 1:
            steps = 1
        if steps > 20:
            steps = 20
        topic['global'] = "kil"
        topic['local'] =  "kvv32"
        topic['client_id'] =  "D1"
        msg = ioant.create_message("RunStepperMotorRaw")
        msg.direction = 1 #COUNTER_CLOCKWISE
        msg.delay_between_steps = 5
        msg.number_of_step = steps
        msg.step_size = 0 #FULL_STEP
        action_text = "Warmer " + str(msg.number_of_steps)
        ioant.publish(msg,topic)
#----------------------------------------------------
    elif action == "heater.decrease":
#----------------------------------------------------
        steps = req.get("result").get("parameters").get("steps")
        if steps < 1:
            steps = 1
        if steps > 20:
            steps = 20
        topic['global'] = "kil"
        topic['local'] =  "kvv32"
        topic['client_id'] =  "D1"
        msg = ioant.create_message("RunStepperMotorRaw")
        msg.direction = 0 #CLOCKWISE
        msg.delay_between_steps = 5
        msg.number_of_step = steps
        msg.step_size = 0 #FULL_STEP
        action_text = "Cooler " + str(msg.number_of_steps)
        ioant.publish(msg,topic)
#----------------------------------------------------
    elif action == "rgb.set":
#----------------------------------------------------
        color = req.get("result").get("parameters").get("color")
        pwm = int(req.get("result").get("parameters").get("pwm"))
        if pwm > pwm_max:
            pwm = pwm_max
        if pwm < 1:
            pwm = 1

        msg = ioant.create_message("Color")

        if color == "red":
            currentRed = pwm
        if color == "green":
            currentGreen = pwm
        if color == "blue":
            currentBlue = pwm

        msg.red = currentRed
        msg.green = currentGreen
        msg.blue = currentBlue
        #action_text = "set rgb " + color + " to " + str(pwm)
        action_text = "set rgb " + str(msg.red) +" "+str(msg.green)+" "+str(msg.blue)
        ioant.publish(msg,topic)
#----------------------------------------------------
    elif action == "rgb.zero":
#----------------------------------------------------
        msg = ioant.create_message("Color")
        currentRed= 1
        currentGreen = 1
        currentBlue = 1

        msg.red = currentRed
        msg.green = currentGreen
        msg.blue = currentBlue
        #action_text = "set rgb " + color + " to " + str(pwm)
        action_text = "zero rgb " + str(msg.red) +" "+str(msg.green)+" "+str(msg.blue)
        ioant.publish(msg,topic)
#----------------------------------------------------
    elif action == "rgb.max":
#----------------------------------------------------
        msg = ioant.create_message("Color")
        currentRed = pwm_max
        currentGreen = pwm_max
        currentBlue = pwm_max

        msg.red = currentRed
        msg.green = currentGreen
        msg.blue = currentBlue
        #action_text = "set rgb " + color + " to " + str(pwm)
        action_text = "max rgb " + str(msg.red) +" "+str(msg.green)+" "+str(msg.blue)
        ioant.publish(msg,topic)
#----------------------------------------------------
    elif action == "rgb.increase":
#----------------------------------------------------
        color = req.get("result").get("parameters").get("color")
        pwm = int(req.get("result").get("parameters").get("pwm"))
        #action_text = "rgb increase " + color + " with " + str(pwm)
        msg = ioant.create_message("Color")
        if color == "red":
            itemp = currentRed + pwm
            if itemp > pwm_max:
                itemp = pwm_max
            if itemp < 1:
                itemp = 1
            currentRed = itemp
        if color == "green":
            itemp = currentGreen + pwm
            if itemp > pwm_max:
                itemp = pwm_max
            if itemp < 1:
                itemp = 1
            currentGreen = itemp
        if color == "blue":
            itemp = currentBlue + pwm
            if itemp > pwm_max:
                itemp = pwm_max
            if itemp < 1:
                itemp = 1
            currentBlue = itemp

        msg.red = currentRed
        msg.green = currentGreen
        msg.blue = currentBlue
        action_text = "increase rgb " + str(msg.red) +" "+str(msg.green)+" "+str(msg.blue)
        ioant.publish(msg,topic)
#----------------------------------------------------
    elif action == "rgb.decrease":
#----------------------------------------------------
        color = req.get("result").get("parameters").get("color")
        pwm = int(req.get("result").get("parameters").get("pwm"))
        #action_text = "rgb decrease " + color + " with " + str(pwm)
        msg = ioant.create_message("Color")
        if color == "red":
            itemp = currentRed - pwm
            if itemp > pwm_max:
                itemp = pwm_max
            if itemp < 1:
                itemp = 1
            currentRed = itemp
        if color == "green":
            itemp = currentGreen - pwm
            if itemp > pwm_max:
                itemp = pwm_max
            if itemp < 1:
                itemp = 1
            currentGreen = itemp
        if color == "blue":
            itemp = currentBlue - pwm
            if itemp > pwm_max:
                itemp = pwm_max
            if itemp < 1:
                itemp = 1
            currentBlue = itemp

        msg.red = currentRed
        msg.green = currentGreen
        msg.blue = currentBlue
        action_text = "decrease rgb " + str(msg.red) +" "+str(msg.green)+" "+str(msg.blue)
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
