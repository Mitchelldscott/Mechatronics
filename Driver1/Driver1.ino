
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"
#include <Servo.h>

// Initialize Motor Control
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); // Create the motor shield object with the default I2C address
Adafruit_DCMotor *myFlywheel = AFMS.getMotor(1); // Flywheel motor attached to M1
Adafruit_DCMotor *myLoader = AFMS.getMotor(2); // Loading motor attached to M1

// Data Processing
String data = ""; 
String num = "";
int motorType = -1; // 0 --> stepper, 1 --> servo
int setpoint = 0;

void setup() {
  // Request for Permission to Begin Program
  int executeProgram = 0;
  Serial.begin(9600);           // set up Serial library at 9600 bps
  while (true) {
    if (Serial.available() > 0) {
      executeProgram = Serial.read();
      if (executeProgram == 121) { // "y" input
        break;
      }
    }
  }

  // Motor Initialization
  AFMS.begin();  // create with the default frequency 1.6KHz


  // Flywheel Motor Initialization
  myFlywheel->setSpeed(127);

  //Loading Motor Initialization
  myLoader->setSpeed(40);
}

void loop() {
  if(Serial.available() > 0) {
      data = Serial.readStringUntil('\n');
      num = "";
      
      // motor type
      num = num + data[0]; 
      motorType = num.toInt();
      num = "";

      // setpoint
      for (int i = 2; i < sizeof(data); i++) {
        num = num + data[i];
      }

      Serial.println(motorType);

      if (motorType == 3) { 
	// firing mechanism
        firingMechanism();
      } else {
        //invalid input
      }
      
  }
  delay(10);

 
void firingMechanism () {
  Serial.println("Check");
  myLoader->setSpeed(40);
  myLoader->run(BACKWARD);
  delay(2000);
  myLoader->run(RELEASE);
  myLoader->setSpeed(80);
  delay(200);
  myLoader->run(FORWARD);
  myFlywheel->run(FORWARD); // Spool up flywheel
  delay(750);
  myLoader->run(RELEASE);
  delay(600);
  myLoader->run(RELEASE); // Kill loader
  myFlywheel->run(RELEASE); // Kill flywheel*/
}
