# Finger Movement Controlled Rhythm Game
Short team name: Ultraviolet-Charon \
Team Members:
- Ethan Dawson (47444908)
- Liam McLean 47400650
- Matthew Moore (48022152)

## Project Overview
This project will be a rhythm game controlled by finger movements and distance. The player will be recorded using a camera, which will be used to determine which fingers they are holding up. An ultrasonic ranger will be used to determine the distance from the controller to the player. This camera feed and the disance between controller and player will be used as the inputs for the game.
During the game, a speaker will play music. This music will depend on the level, with different levels featuring different music tracks. Each music note in a track will be associated with one or more fingers that the player needs to hold up. When the music note is played, the player will need to move their hand, with the correct fingers held up, closer to the ultrasonic ranger. This will be how the player 'plays' a note. Playing the correct notes will increase the player's score, and playing incorrect or no notes will decrease it (or just not increase it). A web dashboard will display incoming notes to inform the player what they need to play. This web dashboard will also display high scores, as well as the camera feed being used to determine their finger positions.

### Key Performance indicators
We will determine the success of the project by the following metrics:
1. Finger detection system can correctly identify the number of fingers held up at least 90% of the time
2. The position detection system can correctly determine distance within +/- 5cm at least 90% of the time
3. The speaker system can properly play music notes in the right order and timing
4. The web dashboard properly displays incoming notes
5. The web dashboard can display the camera feed with limited delay
6. The system properly tracks high scores and displays them on the web dashboard.


## System Architecture
I think this section should also talk about the sensor integration and the wireless network communication / IOT protocols / Web dashboard. If it doesn't flow well put this stuff in its own section
### Hardware
Block diagram of the system
<img width="444" height="350" alt="XIAO_BLE(1)" src="https://github.com/user-attachments/assets/2843d425-ef3d-4051-8f38-68c95a714be5" />

### Software
Top-level flow-chart of software implementation

<p>
<img width="603" height="601" alt="image" src="https://github.com/user-attachments/assets/012cb833-18a6-4cea-adfe-620f86792b57" />
</p>

I don't think this stuff should be in this section but here's some useful resources for the project:
- Datasets: There's a bunch of different ones, just find them if we need one
- Medium Article: https://medium.com/@armanlaliwala/building-a-real-time-finger-counting-system-with-opencv-mediapipe-c9f59d4b739d
- Another article I found. This one has a bunch of code: https://medium.com/@iamramzan/finger-counter-using-opencv-and-mediapipe-a142e7faeae4
- Ultrasound is mentioned about slide 30 of the week 5 lecture. They don't really talk about it much though. We'd need to make sure we have equipment that can actually do it, otherwise we might need to use RSSI or something.
- Kalman filter is also mentioned in week 5 lecture, though I'm sure you guys already know that.

## Algorithms
This project will include data fusion using a Kalman filter to handle inaccuracy or variance in the results from the ultrasonic sensor. Since the ultrasonic sensor will only measure the scalar distance from the player, only a 1-Dimensional Kalman filter will be required. The settings for the Kalman filter (e.g. how much to prioritise the model vs measured results) will depend on the accuracy of readings from the ultrasound sensor. We will experimentally test the device with various Kalman filter settings to find optimal results for the project. Since a rhythm game will require time-sensitive inputs, we will likely prioritise speed of results over precision. The game's design will need to account for this imprecision, for example by using ranges of distances as input rather than precise distances.

To analyze the number of finger the player is holding up a neural network will be used to detect the presence of fingers in an image. This will be done by training a model on images of hands holding up different numbers of finger found online. The training data will be taken from databases of hand images collected for this purpose. When this model is accurate enough it will then be used to determine images that come form the esp32 camera. 

## DIKW Pyramid
<img width="960" height="540" alt="CSSE4011 Project DIKW Diagram" src="https://github.com/user-attachments/assets/c26e4b69-0a60-4c23-bd8a-25e50e01858e" />


The raw data (the camera feed and ultrasonic time between sound wave emitting and receiving) will be used to estimate the player's distance from the ultrasonic ranger and identify the position of the player's fingers. This information will be used to update the Kalman filter model, and determine which of the player's fingers are being held up. These values will then be used as the inputs to control the game.

## Project Management
<img width="1046" height="887" alt="GanttChartImage" src="https://github.com/user-attachments/assets/4d115451-4742-4877-aad7-757afcac1212" />

## Zephyr RTOS Advanced Libraries / Advanced Kernel Features
There is the potential for bluetooth and networking's drivers for the peripherals. The exact libraries are unknown but will involve a more complex connection method between the development board and these peripherals, rather than the simplistic listen and broadcast implementations from previous tasks.

## Team Member Roles
This section will describe the roles of each team member developing the project and justify the team member's involvement. (I'm not sure what exactly 'justifying involvement' means. Maybe it's meant to be why the section(s) we worked on is necessary)
### Ethan Dawson
I will be working primarily on data transfer, working between the speaker, serial connections between devices and the web dashboard. This will involve developing a robust multi threaded system on the xiao development board and a reliable method to send and receive between devices. After this is complete, I will be assisting my other team mates with their tasks. 
### Liam McLean
I will be working on everything to do with finger detection. This will start with connecting the camera and receiving images on a laptop. The images received will then be analyzed using machine learning techniques to determine the number of fingers present in the image. This will be then be passed to the game to determine the players input.
### Matthew Moore
I will work on the ultrasonic sensor, Kalman filter, and the actual game. The ultrasonic sensor will involve creating a driver for the HC-SR04 of functions needed for detecting the distance using the formula:\
distance = (recv_time - emit_time) * 0.5 * speed_of_sound \
The functions defined in this sensor driver will be used with the 1-D Kalman filter to track the player's position. After I have created the Kalman filter I will develop the backend for the game using python. This will involve all of the game mechanics, and controls. For controls, I will call from my Kalman filter code and functions created by my teammates to get the player's current inputs, and translate them into game controls to affect the game state. The state of the game will be output for the web view to display.

## Equipment Required
ESP32-CAM Development Board \
M5 stack speaker (I2S) \
XIAO nRF52840 Sense \
Laptop / PC
