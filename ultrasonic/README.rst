Usage:
Connect GPIO ports 28 and 29 to the hc-sr04 Echo and Trig ports respectively,
 connect ground and either the 5v or 3.3v pin to GND and VCC, then build and flash the board.
 The system seems to be intended for 5v, and 5v seems to work but 3.3v also works so
 using that is recommended for safety.
 If different GPIO pins are needed then modify the overlay file.
 The system will repeatedly print the measured distance, and estimated distance
 and velocity from the Kalman filter model every 0.1 seconds.