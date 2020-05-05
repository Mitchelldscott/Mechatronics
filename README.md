# Mechatronics
MCEN4115/5115 Hogan's Alley Project

# Systems
## Navigation - Mitchell/Thomas
### Arduino D
* Inputs:  
   IR sensor readings,  
   Drive heading from RPi
* Outputs:  
   Motor control signals x 2
### RPi (ubuntu mate 18.04)
* Inputs:  
   Camera reading,  
   Target seen (bool)
* Outputs:  
   Drive heading to drive arduino
## Targeting - Cameron/Graham
### Arduino Top
* Inputs:  
   Target location from Luxonis  
* Outputs:  
   Enable flywheel  
   Actuate lead screw  
   Position Pan/Tilt  
### Luxonis - Riley
* Inputs:  
   Image from Luxonis
* Outputs:  
   Bounding box of target location performed either using CV or ML



