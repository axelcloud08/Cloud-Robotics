//8384 CPR
#include "SoftwareSerial.h"
#include "DualG2HighPowerMotorShield.h"
#include "PololuMaestro.h"
#include "motors_routines.h"
#include "class_servo.h"
#include "Temporizador.h"
#include "Encoders.h"

Temporizador EncodersPrint(100);
Encoder left(18,19);
Encoder rigth(21,20);
MiniMaestro maestro(Serial2);
Motors motor_driver(0,1);
char direction;
int speed;

bool isValid(char* str) {
  if (!isAlpha(str[0])) return false;
  if (str[1] != ',') return false;
  if (!isDigit(str[2])) return false;
  return true;
}

void input_to_data(char* str) {
  if (isValid(str)) {
    direction = str[0];
    speed = str[2] - '0';
  }
}


void left_reading(){
  bool c1_status = digitalRead(left.pin1);
  bool c2_status = digitalRead(left.pin2);

  left.ticks_count += (c1_status == c2_status) ? 1 : -1;
}

void rigth_reading(){
  bool c1_status = digitalRead(rigth.pin1);
  bool c2_status = digitalRead(rigth.pin2);

  rigth.ticks_count += (c1_status == c2_status) ? 1 : -1;
}

Servo back_flipper1(0, 2224, 1008, 1648, 3);
Servo back_flipper2(1, 2224, 1008, 1648, 3);
Servo front_flipper1(2, 2224, 1008, 1648, 3);
Servo front_flipper2(3, 2224, 1008, 1648, 3);
Servo base(4, 2224, 1527, 2224, 10);
Servo codo(5, 2224, 1008, 1008, 10);
Servo cuello(6, 2224, 1008, 1648, 10);
Servo garra(7, 2224,1008, 2224, 10);


void ServosUpdate(){
  back_flipper1.update();
  back_flipper2.update();
  front_flipper1.update();
  front_flipper2.update();
  base.update();
  codo.update();
  cuello.update();
  garra.update();}

void ServosStop(){
  back_flipper1.stop();
  back_flipper2.stop();
  front_flipper1.stop();
  front_flipper2.stop();
  base.stop();
  codo.stop();
  cuello.stop();
  garra.stop();}

void ServosIniciar(){
 back_flipper1.iniciar();
  back_flipper2.iniciar();
  front_flipper1.iniciar();
  front_flipper2.iniciar();
  base.iniciar();
  codo.iniciar();
  cuello.iniciar();
  garra.iniciar();
}

void setup() {
  motor_driver.iniciardriver();
  Serial.begin(9600);
  Serial2.begin(115200);
  Serial.setTimeout(10);

  pinMode(left.pin1, INPUT_PULLUP);
  pinMode(left.pin2, INPUT_PULLUP);
  pinMode(rigth.pin1, INPUT_PULLUP);
  pinMode(rigth.pin2, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(left.pin1), left_reading, CHANGE);
  attachInterrupt(digitalPinToInterrupt(rigth.pin1), rigth_reading, CHANGE);
  ServosIniciar();
}

void loop() {
ServosUpdate(); 

  if(EncodersPrint.termino()){
    EncodersPrint.reiniciar();
    String message = String(millis()) + "," +  String(left.ticks_count) + "," + String(rigth.ticks_count);
    Serial.println(message);
    
  }

  if (Serial.available()) {
    String input = Serial.readString();
    char str[input.length() + 1];
    input.toCharArray(str, sizeof(str));
    input_to_data(str);

     switch(direction){

      case 'w':
      motor_driver.front(speed);
      break;

      case 's':
      motor_driver.back(speed);
      break;

      case 'd':
      motor_driver.rigth(speed);
      break;

      case 'a':
      motor_driver.left(speed);
      break;
      
      case 'b':
      ServosStop();
      motor_driver.stop();
      break;

      case 'c':      
      back_flipper1.go_toMIN();
      back_flipper2.go_toMAX();
      break;

      case 'v':
      back_flipper1.go_toMAX();
      back_flipper2.go_toMIN();
      break;

      case 't':
      front_flipper1.go_toMAX();
      break;

      case 'g':
      front_flipper1.go_toMIN();
      break;

      case 'y':
      front_flipper2.go_toMIN();
      break;

      case 'h':
      front_flipper2.go_toMAX();
      break;

      case 'q':
      front_flipper1.go_toMAX();
      front_flipper2.go_toMIN();
      back_flipper1.go_toMIN();
      back_flipper2.go_toMAX();
      break;

      case 'z':    
      front_flipper1.go_toMAX();
      front_flipper2.go_toMIN();
      break;

      case 'x':     
      front_flipper1.go_toMIN();
      front_flipper2.go_toMAX();
      break;

      case 'u':      
      base.go_toMIN();
      codo.go_toPrepos(1438);
      break;

      case 'n':      
      codo.go_toMIN();
      base.go_toMAX();
      break;
    
      case 'i':
      codo.go_toMAX();
      break;

      case 'k':
      codo.go_toMIN();
      break;
     
      case 'l' :
      cuello.go_toMIN();
      break;

      case 'j':
      cuello.go_toMAX();
      break;

      case 'o':
      garra.go_toMAX();
      break;

      case 'p':
      garra.go_toMIN();
      break;
     
    }

  }
}
