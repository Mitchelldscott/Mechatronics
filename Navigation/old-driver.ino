
#include "motor.h"
#include <Wire.h>

#define Left 0
#define Straight 1
#define Right 2
#define Reverse 3
#define I2C_ADD 0x04

// Cannot pass negatives through i2c so 
// drive striaght tells arduino when to 
// convert a speed to negative
int drive_state = 1;
float l_wheel_vel = 100.0;
float r_wheel_vel = 100.0;
int drive_enabled = 0;
bool update_speed = false;

Motor motor_l(9, 8, 6, 0);
Motor motor_r(12, 13, 11, 1);

void setup() 
{
  Serial.begin(9600);
  Wire.begin(I2C_ADD);
  Wire.onReceive(receive);
}

// i2c block is [enabler byte, left_wheel, right_wheel, state]
// more/less bytes will screw with the values
void receive(int byteCount)
{
  if(Wire.available() == 4)
  {
    drive_enabled = Wire.read();
    l_wheel_vel = Wire.read();
    r_wheel_vel = Wire.read();
    drive_state = Wire.read();
  }
  else
    Serial.println("Error incorrect number of bytes on bus");
  update_speed = true;
  Serial.println(drive_enabled);
}

void loop() {
  // prevent bot from moving
  // in event of target
  if(drive_enabled == 0)
  {
    motor_l.mSpeed = 0;
    motor_r.mSpeed = 0;
  }
  //converts necesary speed to negative
  //if(update_speed)
  //{
    switch(drive_state){
      case Left:
        motor_l.mSpeed = -l_wheel_vel;
        motor_r.mSpeed = r_wheel_vel;
        break;
      case Straight:
        motor_l.mSpeed = l_wheel_vel;
        motor_r.mSpeed = r_wheel_vel;
        break;
      case Right:
        motor_l.mSpeed = l_wheel_vel;
        motor_r.mSpeed = -r_wheel_vel;
        break;
      case Reverse:
        motor_l.mSpeed = -l_wheel_vel;
        motor_r.mSpeed = -r_wheel_vel;
        break;
    }
    update_speed = false;
    Serial.println(motor_l.mSpeed);
    Serial.println(motor_r.mSpeed);
  //}
  
  motor_r.drive();
  motor_l.drive();
}
