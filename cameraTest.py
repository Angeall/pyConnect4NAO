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
        hasRead, img = cap.read()
        if not hasRead:
            print "Image not readable"
            break
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        thresholdedImg = cv2.Canny(gray, 35, 50, L2gradient=True)
        _, contours, h = cv2.findContours(thresholdedImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:
                approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
                print len(approx)
                if len(approx)==5:
                    print "pentagon"
                    cv2.drawContours(img,[cnt],0,255,-1)
                elif len(approx) > 15:
                    print "circle"
                    cv2.drawContours(img,[cnt],0,(0,255,255),-1)
                elif len(approx)==3:
                    print "triangle"
                    cv2.drawContours(img,[cnt],0,(0,255,0),-1)
                elif len(approx)==4:
                    print "square"
                    cv2.drawContours(img,[cnt],0,(0,0,255),-1)
                elif len(approx) == 9:
                    print "half-circle"
                    cv2.drawContours(img,[cnt],0,(255,255,0),-1)
        # newImg = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # thresholdedImg = cv2.inRange(newImg, np.array([cv2.getTrackbarPos("LowH", "Control"),
        #                                                cv2.getTrackbarPos("LowS", "Control"),
        #                                                cv2.getTrackbarPos("LowV", "Control")]),
        #                              np.array([cv2.getTrackbarPos("HighH", "Control"),
        #                                        cv2.getTrackbarPos("HighS", "Control"),
        #                                        cv2.getTrackbarPos("HighV", "Control")]))
        # cv2.erode(thresholdedImg, thresholdedImg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)))
        # cv2.dilate(thresholdedImg, thresholdedImg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)))
        #
        # cv2.dilate(thresholdedImg, thresholdedImg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)))
        # cv2.erode(thresholdedImg, thresholdedImg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)))
        cv2.imshow("Thresholded Image", thresholdedImg)
        cv2.imshow("Original Image", img)

        if cv2.waitKey(1) == 27:
            print "Esc pressed : exit"
            break
    return 0


if __name__ == '__main__':
    test()