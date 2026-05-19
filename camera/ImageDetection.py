import urllib.request
import numpy as np
import cv2
from cvzone.HandTrackingModule import HandDetector

url = "http://192.168.20.74/capture"

detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    try:
        imgResp = urllib.request.urlopen(url)
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)

        hands, img = detector.findHands(img)
        fingers = [0, 0, 0, 0, 0]

        if hands:
            hand = hands[0]
            fingers = detector.fingersUp(hand)
            print(fingers)

        cv2.putText(img, f"Fingers: {sum(fingers)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Hand Detection", img)

        if cv2.waitKey(1) == 27:
            break
    except Exception as e:
        print("Error: ", e)

cv2.destroyAllWindows()
