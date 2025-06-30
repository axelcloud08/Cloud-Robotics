#ifndef SERVO_H
#define SERVO_H

#include "Temporizador.h"
#include <PololuMaestro.h>  
extern MiniMaestro maestro;

class Servo {
  private:
    unsigned int canal;
    unsigned long intervalo;
    Temporizador* timer;
    unsigned int MAX;
    unsigned int MIN;
    unsigned int pulso_meta;
    unsigned int actual;
    unsigned int inicio;

  public:
    Servo(unsigned int canal, unsigned int MAX, unsigned int MIN, unsigned int inicio, unsigned long intervalo);
    void update();
    void iniciar();
    void change_pulse(unsigned int nuevo_pulso);
    void stop();
    void go_toMAX();
    void go_toMIN();
    void go_toPrepos(unsigned int Prepos);
};

#endif
