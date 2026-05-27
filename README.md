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
pip install pygame

### Speaker Setup
Build and flash to the first XIAO nRF52840 Sense the speaker folder

### Ultrasonic Setup
Build and flash to the second XIAO nRF52840 Sense the ultrasonic folder


