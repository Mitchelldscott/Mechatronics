# Mechatronics
MCEN4115/5115 Hogan's Alley Project

# Systems
## Navigation - Mitchell/Thomas
### Arduino D
    Inputs: 
      IR sensor readings,
      Drive heading from RPi
    Outputs:
      Motor control signals x 2
### RPi (ubuntu mate 18.04)
    Inputs:
      Camera reading,
      Target seen (bool)
    Outputs:
      Drive heading to arduino D
## Targeting - Cameron/Graham
### Arduino Top
* Inputs:  
   Target location from Luxonis  
* Outputs:  
   Enable flywheel  
   Actuate lead screw  
   Position Pan/Tilt  

### Luxonis
* TF Model based on ssd_mobilenet_V2 trained for red target (200+ images)
   Inference output contains bounding box metadata used to determine distance from center of image
* Output: **(x,y)** distance from center of image (300,300) with confidence > 0.7



