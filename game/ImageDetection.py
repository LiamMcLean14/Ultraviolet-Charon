import urllib.request
import numpy as np
import cv2
from cvzone.HandTrackingModule import HandDetector

url = "http://10.197.16.114/capture"
detector = HandDetector(detectionCon=0.8, maxHands=1)

def getFingerData():
    fingers = [-1]
    img = -1
    try:
        imgResp = urllib.request.urlopen(url)
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)

        hands, img = detector.findHands(img)
        fingers = [0, 0, 0, 0, 0]

        if hands:
            hand = hands[0]
            fingers = detector.fingersUp(hand)
            #print(fingers)

        cv2.putText(img, f"Fingers: {sum(fingers)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        #cv2.imwrite("fingersMarked.jpg", img)
        #cv2.imshow("Hand Detection", img)

    except Exception as e:
        print("Error: ", e)
    return fingers, img

def showImage():
    try:
        imgResp = urllib.request.urlopen(url)
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)
        cv2.imshow("Image", img)
    except Exception as e:
        print("Error: ", e)

if __name__ == "__main__":
    while True:
        fingers, img = getFingerData()
        print(fingers)
        #showImage()
        if cv2.waitKey(1) == 27:
            break
    cv2.destroyAllWindows()

# Fingers Array Thumb, pointer, middle, ring, pinky


