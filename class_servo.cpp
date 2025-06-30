#include "class_servo.h"

Servo::Servo(unsigned int canal, unsigned int MAX, unsigned int MIN, unsigned int inicio, unsigned long intervalo) {
  this->canal = canal;
  this->timer = new Temporizador(intervalo);
  this->inicio = inicio * 4;
  this->MAX = MAX * 4;
  this->MIN = MIN * 4;
  this->pulso_meta = this->inicio;
  this->actual = this->pulso_meta;
}

void Servo::update() {
  if (actual == pulso_meta) return;
  if (!timer->termino()) return;
  timer->reiniciar();
  if (actual > pulso_meta) actual -= 45;
  else actual += 45;
  maestro.setTarget(canal, actual);
}

void Servo::iniciar() {
  maestro.setTarget(canal, inicio);
}

void Servo::change_pulse(unsigned int nuevo_pulso) {
  pulso_meta = nuevo_pulso;
}

void Servo::stop() {
  pulso_meta = actual;
}

void Servo::go_toMAX() {
  change_pulse(MAX);  
}

void Servo::go_toMIN() {
  change_pulse(MIN);
}

void Servo::go_toPrepos(unsigned int Prepos) {
  change_pulse(Prepos*4);
}
