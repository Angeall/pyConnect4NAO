import cv2
import numpy as np

import src.camera.connect4.connect4 as c4
import src.nao.nao_controller as naoc

__author__ = 'Anthony Rouneau'
robot_ip = "192.168.2.16"
port = 9559

cap = None
nao_c = None


def nothing(x):
    pass


def clean():
    global nao_c, cap
    if nao_c is not None:
        for i in range(7):
            nao_c.disconnect_from_camera(subscriber_id="Connect4NAO_" + str(i))


def get_webcam_image():
    global cap
    if cap is None:
        cap = cv2.VideoCapture(0)
    has_read, img = cap.read()
    if not has_read:
        print "Image not readable"
        return None
    return img


def get_nao_image(camera_num=0):
    global cap, nao_c
    if nao_c is None:
        nao_c = naoc.NAOController(robot_ip, port)
        clean()
        ret = nao_c.connect_to_camera(res=1, fps=30, camera_num=camera_num)
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
        i = 0
        # img = get_webcam_image()
        img = get_nao_image(0)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.medianBlur(gray, 3)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 30,
                                   param1=50, param2=11, minRadius=15, maxRadius=17)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                # draw the outer circle
                cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
                # draw the center of the circle
                cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)
        if circles is not None:
            connect4 = c4.detect_connect4(circles[0], img)
            if connect4 is not None:
                cv2.imshow("Connect4", connect4)
                cv2.waitKey(0)
        cv2.imshow("Original Image", img)
        if cv2.waitKey(1) == 27:
            print "Esc pressed : exit"
            close_camera()
            break
    return 0

def test3():
    dist = 1.0
    while True:
        i = 0
        # img = get_webcam_image()
        img = get_nao_image(0)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.medianBlur(gray, 3)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 11/dist,
                                   param1=60, param2=10.5, minRadius=int(round(5/dist)), maxRadius=int(round(8/dist)))
        if circles is not None:
            # circles = np.uint16(np.around(circles))
            img2 = img.copy()
            for i in circles[0, :]:
                # draw the outer circle
                cv2.circle(img2, (i[0], i[1]), i[2], (0, 255, 0), 2)
                # draw the center of the circle
                cv2.circle(img2, (i[0], i[1]), 2, (0, 0, 255), 2)
            connect4, nb_of_grid_circles = c4.detect_connect4(circles[0], img)
            if connect4 is not None:
                cv2.imshow("Connect4", connect4)
                # cv2.waitKey(0)
            cv2.imshow("Circles detected", img2)
        cv2.imshow("Original picture", img)
        if cv2.waitKey(1) == 27:
            print "Esc pressed : exit"
            close_camera()
            break
    return 0

def test2():
    clean()
    while True:

        img = get_nao_image(0)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        # gray = cv2.medianBlur(gray, 3)
        edges = cv2.Canny(gray, 90, 150, apertureSize=3)
        edges2 = cv2.Canny(gray, 90, 150, apertureSize=3)
        _, cnts, _ = cv2.findContours(edges2, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cnts:
            approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True)*0.01, True)
            # if cv2.contourArea(approx, False) > 40:
            if len(approx) >= 3:
                print len(approx)
                for i in range(len(approx)-1):
                    tuple0 = (approx[i][0][0], approx[i][0][1])
                    tuple1 = (approx[i+1][0][0], approx[i+1][0][1])
                    cv2.line(img, tuple0, tuple1, (0,0,255),2)
                tuple0 = (approx[-1][0][0], approx[-1][0][1])
                tuple1 = (approx[0][0][0], approx[0][0][1])
                cv2.line(img, tuple0, tuple1, (0,0,255),2)
        # lines = cv2.HoughLines(edges, 1.5, np.pi / 360, 175)
        # if lines is not None:
        #     print len(lines)
        #     for line in lines:
        #         rho, theta = line[0]
        #         a = np.cos(theta)
        #         b = np.sin(theta)
        #         x0 = a * rho
        #         y0 = b * rho
        #         x1 = int(x0 + 1000 * (-b))
        #         y1 = int(y0 + 1000 * (a))
        #         x2 = int(x0 - 1000 * (-b))
        #         y2 = int(y0 - 1000 * (a))
        #
        #         cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        #
        cv2.imshow('contours', img)
        cv2.imshow('canny', edges)
        if cv2.waitKey(1) == 27:
            print "Esc pressed : exit"
            close_camera()
            break
    return 0


# def test():
#     while True:
#         #img = get_webcam_image()
#         img = get_nao_image()
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         gray = cv2.GaussianBlur(gray, (3, 3), 0)
#         circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,1,60,
#                             param1=50,param2=11,minRadius=25,maxRadius=31)
#         # circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,1,10,
#         #                     param1=50,param2=10,minRadius=5,maxRadius=8)
#         if circles is not None:
#             circles = np.uint16(np.around(circles))
#             for i in circles[0,:]:
#                 # draw the outer circle
#                 cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
#                 # draw the center of the circle
#                 cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)
#         if circles is not None:
#             print detection.circles_matrix(circles[0], 100)
#             lines = detection.detect_connect_4_lines(circles[0], 85, 200, max_missed=3, min_detected=5)
#             for line in lines:
#                 cv2.rectangle(img, (line[0][0]-20, line[0][1]-20), (line[-1][0]+20, line[-1][1]+20),(255,0,0))
#         # canny = cv2.Canny(gray, 10, 100)
#         # (cnts, _) = cv2.findContours(canny, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2:]
#         # for c in cnts:
#         #     # draw the contour and show it
#         #     cv2.drawContours(img, [c], -1, (0, 0, 255), 2)
#         # lines = 0.
#         # cv2.HoughLines(canny, lines, 1., 1)
#         cv2.imshow("Original Image", img)
#         # cv2.imshow("Original Image", 255-img)
#         if cv2.waitKey(1) == 27:
#             print "Esc pressed : exit"
#             close_camera()
#             break
#     return 0


if __name__ == '__main__':
    test3()
    # test2()

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
