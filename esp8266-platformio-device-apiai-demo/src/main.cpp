///
/// @file   main.cpp
/// @Author Benny Saxen
/// @date   2017-09-14
/// @brief  api.ai demo makers jonkoping
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

int red = 4;
int green = 5;
int blue = 16;

void setup(void){
    //Initialize
    Ioant::GetInstance(on_message);
    pinMode(red,OUTPUT);    // D2
    pinMode(green,OUTPUT);  // D1
    pinMode(blue,OUTPUT);   // D0

    digitalWrite(red,LOW);
    digitalWrite(green,LOW);
    digitalWrite(blue,LOW);

    //Subscribe switch message
    Ioant::Topic subscribe_topic = IOANT->GetConfiguredTopic();
    subscribe_topic.message_type = ProtoIO::MessageTypes::COLOR;
    IOANT->Subscribe(subscribe_topic);
}

void loop(void){
    // Monitors Wifi connection and loops MQTT connection. Attempt reconnect if lost
    IOANT->UpdateLoop();
}

// Function for handling received MQTT messages
void on_message(Ioant::Topic received_topic, ProtoIO* message){

    if (received_topic.message_type == ProtoIO::MessageTypes::COLOR) // SwitchMessage
    {
        digitalWrite(red,LOW);
        digitalWrite(green,LOW);
        digitalWrite(blue,LOW);
        ULOG_DEBUG << "color message received";
        ColorMessage *msg = static_cast<ColorMessage*>(message);
        if(msg->data.red > 0)
        {
           ULOG_DEBUG << "red ";
           digitalWrite(red,HIGH);
        }
        if (msg->data.green > 0)
        {
           ULOG_DEBUG << "green ";
           digitalWrite(green,HIGH);
        }
        if (msg->data.blue > 0)
        {
            ULOG_DEBUG << "blue ";
            digitalWrite(blue,HIGH);
        }
    }
}
