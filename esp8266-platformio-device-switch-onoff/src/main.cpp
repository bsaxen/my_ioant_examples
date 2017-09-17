///
/// @file   main.cpp
/// @Author Benny Saxen
/// @date   2017-09-14
/// @brief  Boiler plate application for onoff switch
/// Turn a device on or off based on switch message
///

#include <ioant.h>
using namespace ioant;
/// @brief on_message() function
/// Function definition for handling received MQTT messages
///
/// @param received_topic contains the complete topic structure
/// @param message is the proto message recieved
///
/// Proto message is casted to appropriate message
///
void on_message(Ioant::Topic received_topic, ProtoIO* message);

// ############################################################################
// Everything above this line is mandatory
// ############################################################################
int onOffPin = 5; // D1

void setup(void){
    //Initialize
    Ioant::GetInstance(on_message);
    pinMode(onOffPin,OUTPUT);
    digitalWrite(onOffPin,LOW);

    //Subscribe switch message
    Ioant::Topic subscribe_topic = IOANT->GetConfiguredTopic();
    subscribe_topic.message_type = ProtoIO::MessageTypes::SWITCH;
    IOANT->Subscribe(subscribe_topic);
}

void loop(void){
    // Monitors Wifi connection and loops MQTT connection. Attempt reconnect if lost
    IOANT->UpdateLoop();
}

// Function for handling received MQTT messages
void on_message(Ioant::Topic received_topic, ProtoIO* message){

    if (received_topic.message_type == ProtoIO::MessageTypes::SWITCH) // SwitchMessage
    {
        ULOG_DEBUG << "switch message received";
        SwitchMessage *msg = static_cast<SwitchMessage*>(message);
        if(msg->data.state == false)
         {
           ULOG_DEBUG << "Set Status to OFF";
           digitalWrite(onOffPin,LOW);
         }
         else if (msg->data.state == true)
         {
           ULOG_DEBUG << "Set Status to ON";
           digitalWrite(onOffPin,HIGH);
         }
         else
         {
           ULOG_DEBUG << "Set Status to unknown";
         };
        //digitalWrite(MS1,LOW);
    }
}
