import argparse
import os
from time import sleep
import numpy as np
import utils.filter as detection
import naoqi
import nao.nao_controller as naoc
import cv2
__author__ = 'Angeall'
robot_ip = "192.168.2.24"
port = 9559

cap = None
nao_c = None

def nothing(x):
    pass


def get_webcam_image():
    global cap
    if cap is None :
        cap = cv2.VideoCapture(0)
        cap.set(3,640)
        cap.set(4,480)
        cap.set(cv2.CAP_PROP_FPS, 2.5)
    hasRead, img = cap.read()
    if not hasRead:
        print "Image not readable"
        return None
    return img


def get_nao_image():
    global cap, nao_c
    if nao_c is None:
        nao_c = naoc.NAOController(robot_ip, port)
        ret = nao_c.connect_to_camera()
        if ret < 0:
            print "Could not open camera"
            return None
    return nao_c.get_image_from_camera()

def close_camera():
    global nao_c, cap
    if nao_c is not None:
        nao_c.disconnect_from_camera()
        return
    else:
        cap.release()
    return


def test():
    while True:
        img = get_webcam_image()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.medianBlur(gray, 3)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,1,15,
                            param1=150,param2=12,minRadius=17,maxRadius=20)
        # circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,1,10,
        #                     param1=50,param2=10,minRadius=5,maxRadius=8)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                # draw the outer circle
                cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
                # draw the center of the circle
                cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)
        if circles is not None:
            lines = detection.detect_connect_4_lines(circles[0], 35, 90, max_missed=2, min_detected=5)
            for line in lines:
                cv2.rectangle(img, (line[0][0]-20, line[0][1]-20), (line[-1][0]+20, line[-1][1]+20),(255,0,0))
        cv2.imshow("Original Image", img)
        if cv2.waitKey(1) == 27:
            print "Esc pressed : exit"
            close_camera()
            break
        sleep(0.300)
    return 0


if __name__ == '__main__':
    test()


# cv2.namedWindow('Control', cv2.WINDOW_AUTOSIZE)
# iLowH = 0
# iHighH = 179
# iLowS = 0
# iHighS = 25
# iLowV = 0
# iHighV = 255
# cv2.createTrackbar("LowH", "Control", iLowH, 179, nothing)
# cv2.createTrackbar("HighH", "Control", iHighH, 179, nothing)
# cv2.createTrackbar("LowS", "Control", iLowS, 255, nothing)
# cv2.createTrackbar("HighS", "Control", iHighS, 255, nothing)
# cv2.createTrackbar("LowV", "Control", iLowV, 255, nothing)
# cv2.createTrackbar("HighV", "Control", iHighV, 255, nothing)
# switch = '0 : OFF \n1 : ON'
# cv2.createTrackbar(switch, 'Control',0,1,nothing)