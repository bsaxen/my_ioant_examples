///
/// @file   main.cpp
/// @Author Benny Saxen
/// @date   2017-12-16
/// @brief  Pin Status
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

/// @brief measure function
/// Measures the time between two pulses
void measure();
// END OF - Custom function definitions

// CUSTOM variables
const byte status_pin = 5;
const byte led_pin = 4;
int toBeUsed;
int current_status = 0;

// END OF - CUSTOM variables

/// END OF - CUSTOM variables

void setup(void){



    Ioant::GetInstance(on_message);

    // ########################################################################
    //    Now he basics all set up. Send logs to your computer either
    //    over Serial or WifiManager.
    // ########################################################################
    CommunicationManager::Configuration loaded_configuration;
    IOANT->GetCurrentConfiguration(loaded_configuration);
    toBeUsed =  loaded_configuration.app_generic_a;

    // Add additional set up code here
    pinMode(status_pin, INPUT);
    pinMode(led_pin, OUTPUT);
    digitalWrite(led_pin,LOW);
}

void loop(void){
    IOANT->UpdateLoop();
    AlarmMessage msg;

    current_status = digitalRead(status_pin);
    if(current_status == LOW)msg.data.meta = "OPENED";
    if(current_status == HIGH)msg.data.meta = "CLOSED";
    ULOG_DEBUG << current_status;

    digitalWrite(led_pin,HIGH);
    bool result = IOANT->Publish(msg);
    ULOG_DEBUG << result << " " << msg.data.meta;

    if(current_status == LOW)
    {
       digitalWrite(led_pin,HIGH);
       delay(100);
       digitalWrite(led_pin,LOW);
    }
    delay(100);
    digitalWrite(led_pin,HIGH);
    delay(100);
    digitalWrite(led_pin,LOW);
}

// Function for handling received MQTT messages
void on_message(Ioant::Topic received_topic, ProtoIO* message){
    WLOG_DEBUG << "Message received! topic:" << received_topic.global  << " message type:" << received_topic.message_type ;
}
