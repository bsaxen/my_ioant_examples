# =============================================
# Benny Saxen
# Date: 2017-06-25
#
# =============================================
from ioant.sdk import IOAnt
import logging
import math
logger = logging.getLogger(__name__)


def publishPhotoTrigger():
    configuration = ioant.get_configuration()
    out_msg = ioant.create_message("Trigger")
    topic = ioant.get_topic_structure()
    topic['top'] = 'live'
    topic['global'] = configuration["publish_topic"]["photo1"]["global"]
    topic['local'] = configuration["publish_topic"]["photo1"]["local"]
    topic['client_id'] = configuration["publish_topic"]["photo1"]["client_id"]
    topic['stream_index'] = 0
    ioant.publish(out_msg, topic)
    topic['top'] = 'live'
    topic['global'] = configuration["publish_topic"]["photo2"]["global"]
    topic['local'] = configuration["publish_topic"]["photo2"]["local"]
    topic['client_id'] = configuration["publish_topic"]["photo2"]["client_id"]
    topic['stream_index'] = 0
    ioant.publish(out_msg, topic)


def getTopicHash(topic):
    res = topic['top'] + topic['global'] + topic['local'] + topic['client_id'] + str(topic['message_type']) + str(topic['stream_index'])
    tres = hash(res)
    tres = tres% 10**8
    return tres

def subscribe_to_topic(par,msgt):
    configuration = ioant.get_configuration()
    topic = ioant.get_topic_structure()
    topic['top'] = 'live'
    topic['global'] = configuration["subscribe_topic"][par]["global"]
    topic['local'] = configuration["subscribe_topic"][par]["local"]
    topic['client_id'] = configuration["subscribe_topic"][par]["client_id"]
    topic['message_type'] = ioant.get_message_type(msgt)
    topic['stream_index'] = configuration["subscribe_topic"][par]["stream_index"]
    print "Subscribe to: " + str(topic)
    ioant.subscribe(topic)
    return


def setup(configuration):
    """ setup function """
    ioant.setup(configuration)

def loop():
    """ Loop function """
    ioant.update_loop()

def on_message(topic, message):
    if topic["message_type"] == ioant.get_message_type("Trigger"):
        print "photo soon"
        publishPhotoTrigger()


def on_connect():
    """ On connect function. Called when connected to broker """
    # There is now a connection
    subscribe_to_topic("pir","Trigger")


# =============================================================================
# Above this line are mandatory functions
# =============================================================================
# Mandatory line
ioant = IOAnt(on_connect, on_message)
