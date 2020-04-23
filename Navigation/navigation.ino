// Communication dummy variable
int byteIn = 0;

// Motor parameters
#include <AFMotor.h>

#define Left 0
#define Straight 1
#define Right 2

// Cannot pass negatives through i2c so 
// drive state tells arduino when to 
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


// IR sensor parameters
const int proxL = A0;
const int proxR = A1;
const int numSamples = 5;
const float minDistance = 6; // minimum sensor distance in inches before modifying movement
const float spFac = 0.5; // factor by which motor speed is modified

float distanceL[numSamples];
float distanceR[numSamples];


void setup() 
{
  pinMode(proxL,INPUT);
  pinMode(proxR,INPUT);
  
  Serial.begin(9600);
}

// incoming byte block is [enabler byte, left_wheel, right_wheel, state]
// more/less bytes will screw with the values
void receive(int byteCount)
{
  if(Serial.available() == 4)
  {
    drive_enabled = Serial.read();
    l_wheel_vel = Serial.read();
    r_wheel_vel = Serial.read();
    drive_state = Serial.read();
  }
  else
//    Serial.println("Error incorrect number of bytes on bus");
  update_speed = true;
//  Serial.println(drive_state);
}

void loop(){

  float measL = removeMaxes(distanceL,numSamples);
  float measR = removeMaxes(distanceR,numSamples);
  float distL = distEst(measL);
  float distR = distEst(measR);
  
  
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


  modifyLR(distL,distR);

  
  if(drive_enabled == 0){
    // prevent bot from moving
    motor_l.setSpeed(0);
    motor_r.setSpeed(0);
  }else{
    // Convert from 0-100 to 0-255
    motor_l.setSpeed(l_wheel_vel*255/100);
    motor_r.setSpeed(r_wheel_vel*255/100);
  }
}









void getDistance(){
  float tempL = 0;
  float tempR = 0;
  for(int i = 0;i<numSamples;i++){
    tempL = analogRead(proxL)*5.0/1023;
    tempR = analogRead(proxR)*5.0/1023;
    distanceL[i] = tempL;
    distanceR[i] = tempR;
    delay(40);
  }
}

float removeMaxes(float arr[], int sizeArr){
  // returns the average of the elements of arr without the 2 highest values
  float max1 = max(arr[0],arr[1]);
  float max2 = min(arr[0],arr[1]);
  float temp = 0;
  float tot = max1+max2;
  for(int i = 2;i<sizeArr;i++){
    temp = arr[i];
    tot += temp;
    if(temp>max1){
      max2 = max1;
      max1 = temp;
    }else if(temp>max2){
      max2 = temp;
    }
  }
  return ((tot-max1-max2)/(sizeArr-2));
}

float distEst(float meas){
  // Voltage to inch conversion for IR Proximity Sensor - Sharp GP2Y0A21YK
  // Effective in the 3" to 10" region (2.94V to 1.17V)
  // Approaching closer than 3" reports longer distances than actual
  // Voltage peaks somewhere in the 2.0" to 2.5" range
  return 11.46598*pow(meas,-1.26165);
}


int modifyLR(float distL, float distR){
//  returns 1 if decreasing L, -1 if decreasing R, 0 if not modifying
//  2 if increasing L, -2 if increasing R. (magnitude changes, not direction)
//  only increases wheels if they are at 0 initially and are required for making a turn
//  float l_wheel_vel = 0.0;
//  float r_wheel_vel = 0.0;
//  float minDistance;
//  int drive_state;
//  const float spFac = 0.5;

  if((distL>minDistance) && (distR>minDistance)){
    // no collision imminent
    return 0;
  }

  // assumes all wheel velocities are non-zero
  if(distR<=minDistance){
    // right side too close
    if(drive_state==Left){
      r_wheel_vel = r_wheel_vel*spFac;
      return -1;
    }else if(drive_state==Straight){
      l_wheel_vel = l_wheel_vel*spFac;
      return 1;
    }else if(drive_state==Right){
      r_wheel_vel = r_wheel_vel*spFac;
      return -1;
    }    
  }else{
    // left side too close
    if(drive_state==Left){
      l_wheel_vel = l_wheel_vel*spFac;
      return 1;
    }else if(drive_state==Straight){
      r_wheel_vel = r_wheel_vel*spFac;
      return -1;
    }else if(drive_state==Right){
      l_wheel_vel = l_wheel_vel*spFac;
      return 1;
    }
  }

  // unknown case, here for robustness
  return 0;

//  // framework for handling cases with one or both wheel velocities == 0
//  if(distR<=minDistance){
//    if(r_wheel_vel==0){
//      
//      return 0;
//    }else if(l_wheel_vel==0){
//      // need to move the left wheel to make the turn
//      if(drive_state==Straight){
//        motor_l.run(BACKWARD);
//      }
//      l_wheel_vel = 40;
//      return 2;
//    }else{
//      
//    }
//  }else{
//    
//  }
  

}
