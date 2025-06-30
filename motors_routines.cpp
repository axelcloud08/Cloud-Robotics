#include "motors_routines.h"
Motors::Motors(bool flip1, bool flip2) {
  this->flip1 = flip1;
  this->flip2 = flip2;
  ptr = speeds;
}

void Motors::iniciardriver(){
  md.calibrateCurrentOffsets();
  delay(10);
  md.enableDrivers();
  md.flipM1(flip1);
  md.flipM2(flip2);
}

void Motors::move(int speed1, int speed2){
  md.setSpeeds(speed1, speed2);
}

void Motors::change_speed(bool dirM1, bool dirM2, int index){
  if (index < 0 || index >= 4) return;
  speedM1 = dirM1 ? -ptr[index] : ptr[index];
  speedM2 = dirM2 ? -ptr[index] : ptr[index];
  md.setSpeeds(speedM1, speedM2);
}

void Motors:: front(int index){
  change_speed(1, 1, index);
}

void Motors:: back(int index){
  change_speed(0, 0, index);
}

void Motors:: left(int index){
  change_speed(0, 1, index);
}

void Motors::rigth(int index){
  change_speed(1, 0, index);
}

void Motors:: stop(){
change_speed(0,0,0);
}
