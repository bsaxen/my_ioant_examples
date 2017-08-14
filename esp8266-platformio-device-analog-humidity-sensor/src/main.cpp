///
/// @file   main.cpp
/// @Author Benny Saxen
/// @date   2017-08-14
/// @brief  Boiler plate application for analog humidity sensor
///

#include <ioant.h>
using namespace ioant;
/// @brief on_message() function
/// Function definition for handling received MQTT messages
///
/// @param received_topic contains the complete topic structure
/// @param payload contains the contents of the message received
/// @param length the number of bytes received
///
void on_message(Ioant::Topic received_topic, ProtoIO* message);

// ############################################################################
// Everything above this line is mandatory
// ############################################################################


/// Custom function definitions
// void TestFunction(int t);
/// END OF - Custom function definitions

///. CUSTOM variables
// int variable_test = 1;
/// END OF - CUSTOM variables

void setup(void){
    //Initialize IOAnt core
    Ioant::GetInstance(on_message);

    // ########################################################################
    //    Now he basics all set up. Send logs to your computer either
    //    over Serial or WifiManager.
    // ########################################################################
    ULOG_DEBUG << "This is a debug message over serial port";
    //WLOG_DEBUG << "This is a debug message over wifi";

}

void loop(void){
    // Monitors Wifi connection and loops MQTT connection. Attempt reconnect if lost
    IOANT->UpdateLoop();

    // Send a Humidity message to itself on topic kConfigTopicGlobal/kConfigTopicLocal

    HumidityMessage h_msg;

    float h = analogRead(A0);
    h = map(h,1000,700,0,100);
    h_msg.data.value = h;
    bool result = IOANT->Publish(h_msg);

    ULOG_DEBUG << "free heap:" << (int)ESP.getFreeHeap();
}

// Function for handling received MQTT messages
void on_message(Ioant::Topic received_topic, ProtoIO* message){
    WLOG_DEBUG << "Message received! topic:" << received_topic.global  << " message type:" << received_topic.message_type ;

}
