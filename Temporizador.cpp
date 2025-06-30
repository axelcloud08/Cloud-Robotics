#include "Temporizador.h"

   Temporizador:: Temporizador(unsigned long tiempo) {
      this->tiempo = tiempo;
      inicial = millis();
    } 

    long Temporizador:: faltante() {
      return tiempo + inicial - millis();
    }

    bool Temporizador:: termino() {
      return faltante() <= 0;
    }

    void Temporizador:: reiniciar() {
      inicial = millis();
    }

    void Temporizador:: cambiar(long nuevo) {
      tiempo = nuevo;
    }

