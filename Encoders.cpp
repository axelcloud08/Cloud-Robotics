#include "Encoders.h"
#include <Arduino.h>  

Encoder:: Encoder(unsigned int pin1, unsigned int pin2){
    this->pin1 = pin1;
    this->pin2 = pin2;
  }
