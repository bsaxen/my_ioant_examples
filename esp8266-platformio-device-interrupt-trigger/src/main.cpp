///
/// @file   main.cpp
/// @Author Benny Saxen
/// @date   2017-06-25
/// @brief  INTERRUPT_TRIGGER
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
const byte interrupt_pin = 5;
const byte led_pin = 4;
int interrupt_counter = 0;
int toBeUsed;

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
    pinMode(interrupt_pin, INPUT_PULLUP);
    pinMode(led_pin, OUTPUT);
    digitalWrite(led_pin,LOW);
    attachInterrupt(interrupt_pin, measure, FALLING);


}

void loop(void){
    IOANT->UpdateLoop();
    TriggerMessage msg;
    msg.data.extra = interrupt_counter;
    ULOG_DEBUG << interrupt_counter;



    //digitalWrite(led_pin,LOW);
    if(interrupt_counter > 0)
    {
      digitalWrite(led_pin,HIGH);
      bool result = IOANT->Publish(msg);
      interrupt_counter  = 0;
      ULOG_DEBUG << result << " " << (int)msg.data.extra;
      delay(300);
      digitalWrite(led_pin,LOW);
    }

}

// Function for handling received MQTT messages
void on_message(Ioant::Topic received_topic, ProtoIO* message){
    WLOG_DEBUG << "Message received! topic:" << received_topic.global  << " message type:" << received_topic.message_type ;
}


// Interrupt function
// Always stored in RAM
void ICACHE_RAM_ATTR measure(){
    digitalWrite(led_pin,HIGH);
    interrupt_counter++;
    digitalWrite(led_pin,LOW);
}
