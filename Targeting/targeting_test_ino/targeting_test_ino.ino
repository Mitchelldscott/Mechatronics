String data = ""; 
String num = "";
int motorType = -1;
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
}

void loop() {
  if(Serial.available() > 0) {
      data = Serial.readStringUntil('\n');
      num = "";
      
      // motor type
      num = num + data[0]; 
      //Serial.println(num);
      motorType = num.toInt();
      num = "";

      // setpoint
      for (int i = 2; i < sizeof(data); i++) {
        num = num + data[i];
      }
      setpoint = num.toInt();

      if (motorType == 0) { // stepper
        //Serial.println(motorType);
        Serial.println(setpoint);
        //stepperMove(setpoint);
      } else if (motorType == 1) { // servo
        Serial.println("MOTOR1");
        //Serial.println(motorType);
        //Serial.println(setpoint);
        //servoMove(setpoint);
      } else if (motorType == 3) { // firing mechanism
        Serial.println("FIRED");
        //Serial.println(motorType);
        //Serial.println(setpoint);
        //firingMechanism();
      } else {
        Serial.println("Invalid");
        //invalid input
      }
      
  }
  delay(10);
}

