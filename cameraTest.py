import numpy as np
import cv2
__author__ = 'Angeall'


def nothing(x):
    pass


def test():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print "Could not open camera"
        return -1
    cv2.namedWindow('Control', cv2.WINDOW_AUTOSIZE)
    iLowH = 0
    iHighH = 179
    iLowS = 0
    iHighS = 25
    iLowV = 0
    iHighV = 255
    cv2.createTrackbar("LowH", "Control", iLowH, 179, nothing)
    cv2.createTrackbar("HighH", "Control", iHighH, 179, nothing)
    cv2.createTrackbar("LowS", "Control", iLowS, 255, nothing)
    cv2.createTrackbar("HighS", "Control", iHighS, 255, nothing)
    cv2.createTrackbar("LowV", "Control", iLowV, 255, nothing)
    cv2.createTrackbar("HighV", "Control", iHighV, 255, nothing)
    switch = '0 : OFF \n1 : ON'
    cv2.createTrackbar(switch, 'Control',0,1,nothing)
    while True:
        hasRead, frame = cap.read()
        if not hasRead:
            print "Image not readable"
            break
        newImg = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        thresholdedImg = cv2.inRange(newImg, np.array([cv2.getTrackbarPos("LowH", "Control"),
                                                       cv2.getTrackbarPos("LowS", "Control"),
                                                       cv2.getTrackbarPos("LowV", "Control")]),
                                     np.array([cv2.getTrackbarPos("HighH", "Control"),
                                               cv2.getTrackbarPos("HighS", "Control"),
                                               cv2.getTrackbarPos("HighV", "Control")]))
        cv2.erode(thresholdedImg, thresholdedImg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)))
        # cv2.dilate(thresholdedImg, thresholdedImg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)))
        #
        # cv2.dilate(thresholdedImg, thresholdedImg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)))
        # cv2.erode(thresholdedImg, thresholdedImg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)))

        cv2.imshow("Thresholded Image", thresholdedImg)
        cv2.imshow("Original Image", frame)

        if cv2.waitKey(1) == 27:
            print "Esc pressed : exit"
            break
    return 0


if __name__ == '__main__':
    test()