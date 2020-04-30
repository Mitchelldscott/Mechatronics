
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"
#include <Servo.h>

// Initialize Motor Control
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); // Create the motor shield object with the default I2C address
//Adafruit_StepperMotor *myStepper = AFMS.getStepper(200, 2); // Connect a stepper motor with 200 steps per revolution (1.8 degree) to motor port #2 (M3 and M4)
//Servo myservo;  // create servo object to control a servo
Adafruit_DCMotor *myFlywheel = AFMS.getMotor(1); // Flywheel motor attached to M1
Adafruit_DCMotor *myLoader = AFMS.getMotor(2); // Loading motor attached to M1


// Global Variable Definition
//long stepperPos;
//long maxStepperAngle = 135;
//int servoAngle;
//int servoPos;
//int servoOffset = 37;
//long steps = 200; // 200 steps per rev
//const int REED_PIN = 9; // Shield v2.3 unused servo pin, Pin 9

// Data Processing
String data = ""; 
String num = "";
int motorType = -1; // 0 --> stepper, 1 --> servo
int setpoint = 0;

void setup() {
  // Request for Permission to Begin Program
  int executeProgram = 0;
  Serial.begin(9600);           // set up Serial library at 9600 bps
  //Serial.print("Execute Program? ");
  while (true) {
    if (Serial.available() > 0) {
      executeProgram = Serial.read();
      if (executeProgram == 121) { // "y" input
        //Serial.println(); 
        break;
      }
    }
  }

  // Motor Initialization
  AFMS.begin();  // create with the default frequency 1.6KHz

  // Stepper Motor Initialization
  //myStepper->setSpeed(10);  // 10 rpm  
  
  // Servo Motor Initialization
  //myservo.attach(10);  // attaches the servo on pin x to the servo object
  //servoMove(0);
  //myservo.write(servoOffset);
  //servoPos = 0;

  // Flywheel Motor Initialization
  myFlywheel->setSpeed(127);

  //Loading Motor Initialization
  //myLoader->setSpeed(127);
  myLoader->setSpeed(50);
  
  // Reed Switch Initialization
  //pinMode(REED_PIN, INPUT_PULLUP);

  // Stepper Absolute Positioning
  // Manually set the Pan-Tilt mechanism to what appears to be the 0 point
  
  //Serial.println("Searching for Pan Absolute Zero...");
  //stepperPos = 0;
  //stepperMove(-30);
  //int overturn = 0;
  //while (true) {
    //stepperMove(stepperPos + 2);
    //Serial.println(stepperPos);
    //if (digitalRead(REED_PIN) == LOW) {
      //stepperPos = 0;
      //Serial.println("Pan Absolute Zero Identified");
      //break;
    //} 
    //if (overturn > 35) {
      //Serial.println("Error: Pan Zero Could Not Be Identified");
      //while (true) {
        // Do not run loop() program
      //}
    //}
    //overturn++;
    //delay(250);
  //}

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
      //setpoint = num.toInt();
      Serial.println(motorType);

      //if (motorType == 0) { // stepper
        //stepperMove(setpoint);
      //} else if (motorType == 1) { // servo
        //servoMove(setpoint);
      //} else if (motorType == 3) { // firing mechanism
      if (motorType == 3) { // firing mechanism
        firingMechanism();
      } else {
        //invalid input
      }
      
  }
  delay(10);

  // Functionality Demo
  /*delay(3000);
  servoMove(-10);
  delay(500);
  servoMove(10);
  delay(500);
  servoMove(0);
  delay(500);
  stepperMove(89);
  delay(650);
  servoMove(10);
  delay(500);
  stepperMove(-90);
  delay(650);
  servoMove(0);
  delay(500);
  stepperMove(45);
  delay(650);
  stepperMove(-45);
  delay(400);
  stepperMove(0);
  while (true) {
    
  }*/
}

/*
void servoMove(int angleIn) {
  //servoAngle = servoOffset + angleIn; // map to actual angles given servo offset
  if (angleIn >= -30 && angleIn <= 30) { // requested angle in bounds
    while (true) {
      if (angleIn > servoPos) {
        myservo.write(servoPos + servoOffset + 1);
        servoPos += 1;
        delay(75);
      } else if (angleIn < servoPos) {
        myservo.write(servoPos + servoOffset - 1);
        servoPos -= 1;
        delay(75);
      } else { // servoPos == angleIn --> goal angle reached
        break;
      }
    }
    delay(50);
  } else {
    //Serial.println("Unreachable servo angle.");
  }
}

void stepperMove(long angleIn) {
  // directionIn is either FORWARD (1) or BACKWARD (0)
  // steptype is either SINGLE, DOUBLE, INTERLEAVE, or MICROSTEP
  // 0 is absolute center, accepts positive and negative values

  long trueAngle = angleIn;
  
  // Correct angleIn to operable value
  while (true) {
    if (angleIn >= 360) {
      angleIn -= 360;
    } else if (angleIn < 0) {
      angleIn += 360;
    } else {
      break;
    }
  }

  // Determine stepper direction, steps required
  // Execute stepper move
  if ( (angleIn <= maxStepperAngle) || (angleIn >= 360-maxStepperAngle) ) { // angleIn within operating bounds [-maxStepperAngle, maxStepperAngle]
    if (abs(angleIn - stepperPos) <= 180) { // shortest direction identified
      if (angleIn >= stepperPos) { // CW
//        Serial.print("1 CW : ");
//        Serial.println(round((angleIn - stepperPos)*steps/360.0));
        myStepper->step(round((angleIn - stepperPos)*steps/360.0), BACKWARD, DOUBLE);
      } else { // angleIn < stepperPos) --> CCW
//        Serial.print("2 CCW : ");
//        Serial.println(round((stepperPos - angleIn)*steps/360.0));
        myStepper->step(round((stepperPos - angleIn)*steps/360.0), FORWARD, DOUBLE);
      }
    } else { // shortest direction opposite direction
      if (angleIn >= stepperPos) { // CCW
//        Serial.print("3 CCW : ");
//        Serial.println(round((360 - angleIn + stepperPos)*steps/360.0));
        myStepper->step(round((360 - angleIn + stepperPos)*steps/360.0), FORWARD, DOUBLE);
      } else { // angleIn < stepperPos) --> CW
//        Serial.print("4 CW : ");
//        Serial.println(round((360 - stepperPos + angleIn)*steps/360.0));
        myStepper->step(round((360 - stepperPos + angleIn)*steps/360.0), BACKWARD, DOUBLE);
      }
    }
    // Update current stepper position
    stepperPos = angleIn;
  } else if (trueAngle > maxStepperAngle) { // Go to maxStepperAngle
//    Serial.print("5 CW : ");
//    Serial.println(round((maxStepperAngle - stepperPos)*steps/360.0));
    myStepper->step(round((maxStepperAngle - stepperPos)*steps/360.0), BACKWARD, DOUBLE); // CW to maxStepperAngle
    // Update current stepper position
    stepperPos = maxStepperAngle;
  } else if (trueAngle < -maxStepperAngle) { // Go to -maxStepperAngle
//    Serial.print("6 CCW : ");
//    Serial.println(round((stepperPos - (360-maxStepperAngle))*steps/360.0));
    myStepper->step(round((stepperPos - maxStepperAngle)*steps/360.0), FORWARD, DOUBLE); // CCW to maxStepperAngle
    // Update current stepper position
    stepperPos = 360 - maxStepperAngle;
  }

  delay(100);
}
*/
void firingMechanism () {  /////////////////////REQUIRES FURTHER DEVELOPMENT
  Serial.println("Check");
  myLoader->run(BACKWARD);
  //delay(710);
  delay(1600);
  myLoader->run(RELEASE);
  delay(2000);
  myLoader->run(FORWARD);
  //delay(360);
  myFlywheel->run(FORWARD); // Spool up flywheel
  delay(1600);
  myLoader->run(RELEASE);
  //myLoader->run(BACKWARD); // Move loader to rear (permits projectile loading)
  //delay(1650);
  //myLoader->run(RELEASE); // Switch loader directions
  //delay(100);
  //myFlywheel->run(FORWARD); // Spool up flywheel
  //delay(1000);
  //myLoader->run(FORWARD); // Move loader to front (loads projectile)
  delay(500);
  myLoader->run(RELEASE); // Kill loader
  myFlywheel->run(RELEASE); // Kill flywheel*/
}
