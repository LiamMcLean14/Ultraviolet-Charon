# Finger Movement Controlled Rhythm Game
## Running the Game
To play the game navigate to the game directoy and run the game.py file\
``cd game``\
``python game.py``


## Setup
### Camera Network
In the camera/CameraWebServer/CameraWebServer.ino\
Replace the wifiname and passowrd with your local values, line 15,16\
const char *ssid = "wifiname";\
const char *password = "password";\
Upload updated file to ESP-32 Camera

### Dependencies
pip install opencv-python\
pip install cvzone\
pip install mediapipe==0.10.14\
pip install pygame\
pip install wave\
pip install bleak\
pip install influxdb_client

### Speaker Setup
Build and flash to the first XIAO nRF52840 Sense the speaker folder

### Ultrasonic Setup
Connect GPIO ports 28 and 29 to the hc-sr04 Echo and Trig ports respectively,
connect ground and either the 5v or 3.3v pin to GND and VCC, then build and flash the board to the second XIAO nRF52840 Sense.
The system seems to be intended for 5v, and 5v seems to work but 3.3v also works so
using that is recommended for safety.
If different GPIO pins are needed then modify the overlay file.
The system will repeatedly print the measured distance, and estimated distance
and velocity from the Kalman filter model every 0.1 seconds to be read by the laptop.

