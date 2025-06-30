#ifndef MOTORS_ROUTINES_H
#define MOTORS_ROUTINES_H

#include <Arduino.h>
#include "DualG2HighPowerMotorShield.h"

class Motors {
private:
  DualG2HighPowerMotorShield18v22 md;
  bool flip1, flip2;
  int speeds[4] = {0, 400, 300, 80};
  int* ptr;
  int speedM1;
  int speedM2;

public:
  Motors(bool flip1, bool flip2);
  void iniciardriver();
  void move(int speed1, int speed2);
  void change_speed(bool dirM1, bool dirM2, int index);
  void front(int index);
  void back(int index);
  void left(int index);
  void rigth(int index);
  void stop();
};


#endif
