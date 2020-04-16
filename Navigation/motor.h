
class Motor
{
  public:
    float mSpeed;
    int IN1;
    int IN2;
    int PWM;
    int isRight;

    Motor(int in1, int in2, int pwm, int is_right)
    {
      mSpeed = 0;
      IN1 = in1;
      IN2 = in2;
      PWM = pwm;
      pinMode(IN1, OUTPUT);
      pinMode(IN2, OUTPUT);
      pinMode(PWM, OUTPUT);
      if(is_right)
        isRight = 1;
    }

    void drive()
    {
      if(mSpeed > 0)
      {
        digitalWrite(IN1, isRight); // drive forward
        digitalWrite(IN2, !isRight);
      }
      else if (mSpeed < 0)
      {
        digitalWrite(IN1, !isRight); // drive backwards
        digitalWrite(IN2, isRight);
      }
      else
      {
        digitalWrite(IN1, 0);
        digitalWrite(IN2, 0);
      }
      analogWrite(PWM, abs(mSpeed));
    }
};
