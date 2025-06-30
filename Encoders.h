#ifndef ENCODERS_H
#define ENCODERS_H

class Encoder{
  public:
   unsigned int pin1;
   unsigned int pin2;
   volatile long ticks_count;
    Encoder(unsigned int pin1, unsigned int pin2);
};

#endif
