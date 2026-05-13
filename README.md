# Finger Movement Controlled Game
Short team name: Ultraviolet-Charon \
Team Members:
- Ethan Dawson (47444908)
- Liam McLean 47400650
- Matthew Moore (48022152)

## Project Overview
This project will be a game controlled by finger movements and distance.
The player will be recorded using a camera (Maybe specify which), which will be used to determine how many fingers they are holding up.
The player's distance from the camera will also be determined using ultrasound (I think).
During the game, speakers will play music... (Explain how the music will be used). 
The game will have different levels featuring different music tracks.
The levels will be selected through a python program (Probably give me info here)
During the game, the camera feed will be displayed to a computer web dashboard.
This web dashboard will also display the player's high scores.

### Key Performance indicators
We will determine the success of the project by the following metrics:
1. Finger detection system can correctly identify the number of fingers held up at least 90% of the time
2. The position detection system can correctly determine distance within +/- 5cm at least 90% of the time
3. The speaker system can properly play music notes in the right order and timing
4. The web dashboard can display the camera feed with limitted delay
5. The system properly tracks high scores and displays them on the web dashboard.
6. The game systems (e.g. level select) are easy to use and work without errors.

## System Architecture
I think this section should also talk about the sensor integration and the wireless network communication / IOT protocols / Web dashboard. If it doesn't flow well put this stuff in its own section
### Hardware
Hardware Diagram of the System
<img width="998" height="790" alt="image" src="https://github.com/user-attachments/assets/b02d4fd4-7635-4733-8c7c-8e86d402e85c" />

### Software
Top-level flow-chart of software implementation

I don't think this stuff should be in this section but here's some useful resources for the project:
- Datasets: There's a bunch of different ones, just find them if we need one
- Medium Article: https://medium.com/@armanlaliwala/building-a-real-time-finger-counting-system-with-opencv-mediapipe-c9f59d4b739d
- Another article I found. This one has a bunch of code: https://medium.com/@iamramzan/finger-counter-using-opencv-and-mediapipe-a142e7faeae4
- Ultrasound is mentioned about slide 30 of the week 5 lecture. They don't really talk about it much though. We'd need to make sure we have equipment that can actually do it, otherwise we might need to use RSSI or something.
- Kalman filter is also mentioned in week 5 lecture, though I'm sure you guys already know that.

## Algorithms
Due to the possible inaccuracy of measurements of the distance from the player to the camera, a 1-D Kalman filter will be used to more accurately approximate the distance.

Also mention machine learning approaches if we use ML

## DIKW Pyramid
Something like
- Data: Raw camera feed, Ultrasound values
- Information: Estimated Distance measurement from camera, position of fingers in camera feed
- Knowledge: Number of fingers being currently held up, Updated Kalman filter model of camera distance
- Wisdom: Actions controlling the game

Needs to be in an actual diagram though

## Project Management
We need to allocate tasks between us and plan out a timeline to get stuff done by \
I think they also want a gantt chart of the timeline. Or some other way of visualising it.
The milestone criteria doesn't even mention this so we probably don't have to go too in-depth on it.

## Zephyr RTOS Advanced Libraries / Advanced Kernel Features
~~I don't even know what an 'advanced' library is, how am I supposed to know what we're gonna use?~~ \
Maybe there's drivers for the peripherals. If so they might count as advanced libraries

## Team Member Roles
This section will describe the roles of each team member developing the project and justify the team member's involvement. (I'm not sure what exactly 'justifying involvement' means. Maybe it's meant to be why the section(s) we worked on is necessary)
### Ethan Dawson
I will primarily work on the speakers and the web app, I expect these tasks to be completed quickly so will then move onto assisting my team mates with their tasks. 
### Liam McLean
I will work on the camera and the AI detection, 
### Matthew Moore
Game Design and Ultra Sonic 

#### Later. 
## Equipment Required
- Camera (List exact type)
- Speakers (List exact type)
- Xiao seeed thing
- Laptop
