#ifndef TEMPORIZADOR_H
#define TEMPORIZADOR_H

#include <Arduino.h>
class Temporizador {
  private:
    unsigned long tiempo;
    unsigned long inicial = millis();

  public:
    Temporizador(unsigned long tiempo);

    long faltante();

    bool termino();

    void reiniciar();

    void cambiar(long nuevo);
    
};
#endif
