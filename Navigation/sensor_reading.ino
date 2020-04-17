const int prox1 = A4;
const int numSamples = 5;

float distance[numSamples];

void setup(){
  pinMode(prox1,INPUT);
  
  Serial.begin(9600);
}

void loop(){
  getDistance();
  float meas1 = removeMaxes(distance,numSamples);
  float dist1 = distEst(meas1);
  Serial.print("Volts:  ");
  Serial.print(meas1);
  Serial.print("   Estimated Distance:  ");
  Serial.println(dist1);
}

void getDistance(){
  float temp = 0;
  for(int i = 0;i<numSamples;i++){
    temp = analogRead(prox1)*5.0/1023;
    distance[i] = temp;
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
