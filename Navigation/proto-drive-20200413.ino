
#include <AFMotor.h>
#include <Wire.h>

#define Left 0
#define Straight 1
#define Right 2
#define I2C_ADD 0x04

// Cannot pass negatives through i2c so 
// drive straight tells arduino when to 
// convert a speed to negative
int drive_state = 1;
float l_wheel_vel = 0.0;
float r_wheel_vel = 0.0;
int drive_enabled = 0;
bool update_speed = false;


// lowest power consumption frequency is 1 kHz "MOTOR12_1KHZ"
// quietest running is 64 kHz "MOTOR12_64KHZ"
// other options are 8 and 2 kHz
AF_DCMotor motor_l(3, MOTOR12_1KHZ); // motor 3, frequency spec is ignored for not 1 or 2
AF_DCMotor motor_r(4, MOTOR12_1KHZ); // motor 4

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
  Serial.println(drive_state);
}

void loop() {
  // prevent bot from moving
  // in event of target
  if(drive_enabled == 0)
  {
    motor_l.setSpeed(0);
    motor_r.setSpeed(0);
  }
  //changes motor directions as specified by drive_state
  if(update_speed)
  {
    switch(drive_state){
      case Left:
        motor_l.run(BACKWARD);
        motor_r.run(FORWARD);
        break;
      case Straight:
        motor_l.run(FORWARD);
        motor_r.run(FORWARD);
        break;
      case Right:
        motor_l.run(FORWARD);
        motor_r.run(BACKWARD);
        break;
    }
    update_speed = false;
  }

  // Convert from 0-100 to 0-255
  motor_l.setSpeed(l_wheel_vel*255/100);
  motor_r.setSpeed(r_wheel_vel*255/100);
}
