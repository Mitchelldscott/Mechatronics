#include <AFMotor.h>
#include "IRRL.h"

#define Left 0
#define Forward 1
#define Right 2
#define Backward 3
#define Nsamples 5
#define Cycle_time 100 // needs to increase as more functionality is added
/*
#define Bin_size 4
#define Nbins 5
#define CstateSize 3
#define Nstates 64
#define Nactions 9
#define Gamma 0.5
#define Epsilon 4.0
#define Decay 0.2*/

// initialize Q-Learning tools
/*QLearner learner(Gamma, Epsilon, Decay);
int state_space[Nstates][2];
int action_space[Nactions][2] = {{0.5, 2.0}, {0.5, 1.0}, {0.5, 0.5}, {1.0, 0.5}, {2.0, 0.5}, {1.0, 1.0}, {1.0, 2.0}, {2.0, 1.0}, {2.0, 2.0}};
int policy[Nstates] = {0};
float p_table[Nactions][Nstates] = {0};

void init_state_space(int state_space[Nstates][2]){
  int c_state[3] = {0,0,0};
  for(int s = 0; s < nStates; s++){
    memcpy(state_space[s], c_state, c_state + CstateSize);
    c_state[0] = (c_state[0] + 1) % 4;
    if(s >= c_state[1] * 4)
      c_state[1] = (c_state[1] + 1) % 4;
  }
}

int c_state2state(int c_state[CstateSize]){
  for(int s = 0; s < Nstates; s++){
    if(c_state[0] == state_space[s][0] && c_state[1] == state_space[s][1])
      return s;
  }
  // this should never execute
  return -1;
}
*/
class IR_Sensors{
   public:
    float l_data[Nsamples];
    float r_data[Nsamples];
    int current;
    int l_prox;
    int r_prox;
    float min1;
    float min2;
    IR_Sensors(int l,int r, float m1, float m2)
    {
      current = 0;
      l_prox = l;
      r_prox = r;
      min1 = m1;
      min2 = m2;
      
    }
    
    float read_sensors()
    {
      current = (current + 1) % Nsamples;
      l_data[current] = analogRead(l_prox) * 5.0 / 1023;
      r_data[current] = analogRead(r_prox) * 5.0 / 1023;
    }

    int get_adjustment(float adjustment[2]){
      read_sensors();
      Serial.print("Left ");
      Serial.println(l_data[current]);
      Serial.print("Right ");
      Serial.println(r_data[current]);
      int i = 0;
      if(l_data[current] >= min2 || r_data[current] >= min2){
        adjustment[0] = 0.5;
        adjustment[1] = 0.5;
        return 3;
      }
      if(l_data[current] >= min1){
        adjustment[1] = 0.5;
        i ++;
      }
      if(r_data[current] >= min1){
        adjustment[0] = 0.5;
        i++;
      }
      if(i == 2){
        return 3;
      }
      return 1;
    }
    
}irs(A5, A0, 1.2, 2.5);

// object for the robot
//  just to clean up the file
struct Robot {
  int drive_state;
  float l_wheel_vel;
  float r_wheel_vel;
  int drive_enabled;
  bool update_speed;
  // IR sensor parameters
  IR_Sensors ir;
} bot = {1, 0.0, 0.0, 0, false, irs};

void get_ir_adjustment(float adjustment[2]){
  bot.drive_state = bot.ir.get_adjustment(adjustment);
  bot.update_speed = true;
}
/*
float reward(int state){
    return (3 - bot.ir.l_data[bot.ir.prev]) + (3 - bot.ir.r_data[bot.ir.prev]) / 6;
}
*/
// lowest power consumption frequency is 1 kHz "MOTOR12_1KHZ"
// quietest running is 64 kHz "MOTOR12_64KHZ"
// other options are 8 and 2 kHz
AF_DCMotor motor_l(3, MOTOR12_64KHZ);
AF_DCMotor motor_r(4, MOTOR12_64KHZ);

float start = 0;
float fin = 0;
//int action = -1;
//int state = -1;
//int n_state = -1;

void setup() 
{
  //init_state_space(state_space);
  pinMode(bot.ir.l_prox,INPUT);
  pinMode(bot.ir.r_prox,INPUT);  
  Serial.begin(9600);
}

// reads [drive_enable, drive_heading] 
//  and converts the heading into a state/wheel velocities
void serialEvent()
{
  if(Serial.available() == 2)
  {
    bot.drive_enabled = Serial.read();
    int heading = Serial.read();
    switch(heading){
      case 0:
        bot.l_wheel_vel = 75;
        bot.r_wheel_vel = 75;
        bot.drive_state = 0;
        break;
      case 1:
        bot.l_wheel_vel = 50;
        bot.r_wheel_vel = 100;
        bot.drive_state = 1;
        break;
      case 2:
        bot.l_wheel_vel = 75;
        bot.r_wheel_vel = 75;
        bot.drive_state = 1;
        break;
      case 3:
        bot.l_wheel_vel = 100;
        bot.r_wheel_vel = 50;
        bot.drive_state = 1;
        break;
      case 4:
        bot.l_wheel_vel = 75;
        bot.r_wheel_vel = 75;
        bot.drive_state = 2;
        break;
    }
    /*
    Serial.print("Drive_state: ");
    Serial.println(bot.drive_state);
   */
    bot.update_speed = true;
  }
}

void loop(){
  start = millis();
  //changes motor directions as specified by drive_state
  serialEvent();
  float adjustment[2] = {1,1};
  get_ir_adjustment(adjustment);
  if(bot.update_speed)
  {
    switch(bot.drive_state){
      case Left:
        motor_l.run(BACKWARD);
        motor_r.run(FORWARD);
        break;
      case Forward:
        motor_l.run(FORWARD);
        motor_r.run(FORWARD);
        break;
      case Right:
        motor_l.run(FORWARD);
        motor_r.run(BACKWARD);
        break;
      case Backward:
        motor_l.run(BACKWARD);
        motor_r.run(BACKWARD);
    }
    bot.update_speed = false;
  }
  // create complex state
  //int c_state[CstateSize] = {(int)(bot.ir.l_data[bot.ir.prev] + 0.5), (int)(bot.ir.l_data[bot.ir.prev] + 0.5), bot.drive_state};
  // compress into state
  //state = n_state;
  //n_state = c_state2state(c_state);
  // send state to model
  //learner.track_event(state, action, n_state, p_table);
  // create policy
  //learner.make_policy(reward, p_table, policy);
  //action = policy[n_state];
  //int adjustment[2] = {action_space[action][0], action_space[action][1]};
  if(bot.drive_enabled == 0)
  {
    // prevent bot from moving
    motor_l.run(RELEASE);
    motor_r.run(RELEASE);
    motor_l.setSpeed(0);
    motor_r.setSpeed(0);
  }
  else
  {
    // Convert from 0-100 to 0-255
    motor_l.setSpeed(bot.l_wheel_vel * 255 / 100 * adjustment[0]);
    motor_r.setSpeed(bot.r_wheel_vel * 255 / 100 * adjustment[1]);
  }
  fin = millis();
  float duration = fin - start;
  float spare_t = max(0, duration - Cycle_time);
  delay(spare_t);
}
