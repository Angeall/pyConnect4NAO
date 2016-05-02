from time import sleep

import cv2
import numpy as np
from hampy import detect_markers

import connect4.detector.front_holes as c4
import connect4.detector.upper_hole as upper_hole
from connect4.connect4handler import Connect4Handler
from connect4.connect4tracker import Connect4Tracker
from connect4.model.default_model import DefaultConnect4Model
from nao import data
from nao.controller.motion import MotionController
from nao.controller.tracking import TrackingController
from nao.controller.video import VideoController

__author__ = 'Anthony Rouneau'

cap = None
nao_video = None
nao_motion = None
nao_tracking = None


def nothing(x):
    pass


def clean():
    global nao_video, cap
    if nao_video is not None:
        for i in range(7):
            nao_video.disconnectFromCamera(subscriber_id="Connect4NAO_" + str(i))


def get_webcam_image():
    global cap
    if cap is None:
        cap = cv2.VideoCapture()
    has_read, img = cap.read()
    if not has_read:
        print "Image not readable"
        return None
    return img


def get_nao_image(camera_num=0, res=1):
    global nao_video, nao_motion, nao_tracking
    if nao_video is None:
        nao_video = VideoController()
        nao_motion = MotionController()
        nao_tracking = TrackingController()
        clean()
        ret = nao_video.connectToCamera(res=res, fps=30, camera_num=camera_num)
        if ret < 0:
            print "Could not open camera"
            return None
    return nao_video.getImageFromCamera()


def close_camera():
    global nao_video, cap
    if nao_video is not None:
        nao_video.disconnectFromCamera()
        return
    else:
        cap.release()
    return


def draw_circles(img, circles):
    img2 = img.copy()
    for i in circles:
        # draw the outer circle
        cv2.circle(img2, (i[0], i[1]), i[2], (0, 255, 0), 2)
        # draw the center of the circle
        cv2.circle(img2, (i[0], i[1]), 2, (0, 0, 255), 2)
    return img2


def test():
    connect4_model = DefaultConnect4Model()
    c4_detector = c4.FrontHolesDetector(connect4_model)
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
            try:
                c4_detector.runDetection(circles[0], img=img)
                connect4 = c4_detector.getPerspective()
                cv2.imshow("Connect4Handler", connect4)
                print c4_detector.homography
            except c4.CircleGridNotFoundException:
                pass
        cv2.imshow("Original Image", img)
        if cv2.waitKey(1) == 27:
            print "Esc pressed : exit"
            close_camera()
            break
    return 0


def test3():
    myc4 = Connect4Handler(get_nao_image)
    dist = 0.5
    sloped = False
    while True:
        try:
            myc4.detectFrontHoles(dist, sloped, tries=4)
            cv2.imshow("Connect4Handler", myc4.front_hole_detector.getPerspective())
        except c4.FrontHolesGridNotFoundException:
            pass
        img2 = draw_circles(myc4.img, myc4.circles)
        cv2.imshow("Circles detected", img2)
        cv2.imshow("Original picture", myc4.img)
        if cv2.waitKey(1) == 27:
            print "Esc pressed : exit"
            close_camera()
            break
        sleep(0.5)
    return 0


def tracker_test():
    c4_detector = c4.FrontHolesDetector(Connect4Handler(get_nao_image))
    dist = 1.
    sloped = False
    min_radius, max_radius = Connect4Handler(get_nao_image).computeMinMaxRadius(dist, sloped)
    pixel_error_margin = Connect4Handler(get_nao_image).computeMaxPixelError(min_radius)
    while True:
        i = 0
        # img = get_webcam_image()
        img = get_nao_image(0)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        # gray = cv2.medianBlur(gray, 3)
        # max_radius = int(round(8/dist))
        # min_radius = int(round(5/dist))
        param2 = 10.5
        if sloped:
            param2 = 8
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 11 / dist,
                                   param1=60, param2=param2, minRadius=min_radius, maxRadius=max_radius)
        if circles is not None:
            # circles = np.uint16(np.around(circles))
            img2 = img.copy()
            for i in circles[0, :]:
                # draw the outer circle
                cv2.circle(img2, (i[0], i[1]), i[2], (0, 255, 0), 2)
                # draw the center of the circle
                cv2.circle(img2, (i[0], i[1]), 2, (0, 0, 255), 2)
            cv2.imshow("Circles detected", img2)
            try:
                c4_detector.runDetection(circles[0], pixel_error_margin=pixel_error_margin,
                                         img=img)
                connect4 = c4_detector.getPerspective()
                # print repr(np.float32(np.array(Connect4Handler(get_nao_image).reference_mapping[(0, 0)])))
                # print repr(c4_detector.homography)
                print cv2.perspectiveTransform(
                    np.float32(Connect4Handler(get_nao_image).reference_mapping[(0, 0)]).reshape(1, -1, 2),
                    c4_detector.homography).reshape(-1, 2)
                rows, cols, _ = img.shape
                # print c4_detector.homography
                # print cv2.warpPerspective(np.uint8(np.array([[Connect4Handler(get_nao_image).reference_mapping[(3, 3)]]])),
                #                           c4_detector.homography, (1, 1), flags=cv2.WARP_INVERSE_MAP)
                cv2.imshow("Connect4Handler", connect4)
            except c4.CircleGridNotFoundException:
                pass
        cv2.imshow("Original picture", img)
        if cv2.waitKey(1000) == 27:
            print "Esc pressed : exit"
            close_camera()
            break
        sleep(0.5)
    return 0


def test2():
    clean()
    imgs = []
    uhc = upper_hole.UpperHoleDetector(DefaultConnect4Model())
    j = 1
    while True:
        img = get_nao_image(1)
        # img = cv2.imread("test_img/img" + str((j % 154) + 1) + ".png")
        # imgs.append(img.copy())
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (1, 1), 0)
        # gray = cv2.medianBlur(gray, 1)
        edges = cv2.Canny(gray, 195, 200, apertureSize=3)
        edges2 = edges.copy()
        _, cnts, _ = cv2.findContours(edges2, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # lines = cv2.HoughLines(edges, 1.5, np.pi / 360, 133)
        # if lines is not None:
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
        #         cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 1)
        rectangles = []
        for cnt in cnts:
            approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True) * 0.01, True)
            # if cv2.contourArea(approx, False) > 40:
            if len(approx) >= 3:
                # print approx
                for i in range(len(approx) - 1):
                    tuple0 = (approx[i][0][0], approx[i][0][1])
                    tuple1 = (approx[i + 1][0][0], approx[i + 1][0][1])
                    # cv2.line(img, tuple0, tuple1, (0, 0, 255), 2)
                tuple0 = (approx[-1][0][0], approx[-1][0][1])
                tuple1 = (approx[0][0][0], approx[0][0][1])
                # cv2.line(img, tuple0, tuple1, (0, 0, 255), 2)
                rect = cv2.minAreaRect(cnt)
                # rectArea = abs(rect[1][0] * rect[1][1])
                box = cv2.boxPoints(rect)
                cntArea = abs(cv2.contourArea(cv2.convexHull(approx), False))
                box = np.int0(box)
                # rectArea = cv2.contourArea(np.array(box), False)
                rectArea = rect[1][0] * rect[1][1]
                if abs(rectArea) <= 1.4 * abs(cntArea):
                    rectangles.append(rect)
                    cv2.drawContours(img, [box], 0, (255, 0, 0), 2)
        uhc.runDetection(rectangles, None)
        for hole in uhc.holes:
            box = cv2.boxPoints(hole)
            box = np.int0(box)
            cv2.drawContours(img, [box], 0, (0, 255, 0), 5)
        cv2.imshow('contours', img)
        cv2.imshow('canny', edges)
        if cv2.waitKey(500) == 27:
            print "Esc pressed : exit"
            close_camera()
            i = 0
            for img in imgs:
                i += 1
                cv2.imwrite("test_img/img" + str(i) + ".png", img)
            break
        j += 1
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

def test4():
    global nao_video, nao_tracking, nao_motion
    myc4 = Connect4Handler(get_nao_image)
    while True:
        img = get_nao_image(1)
        cv2.imshow("TEST", img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        cv2.imshow("Contour", myc4.getUpperHoleCoordinates(gray, gray.copy()))
        if cv2.waitKey(1) == 27:
            print "Esc pressed : exit"
            close_camera()
            break


def testBarCode():
    while True:
        img = get_nao_image(1, res=2)

        markers = detect_markers(img)

        for m in markers:
            m.draw_contour(img)
            cv2.putText(img, str(m.id), tuple(int(p) for p in m.center),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            print str(m.id) + " " + str(m.contours)
        print
        cv2.imshow('live', img)
        if cv2.waitKey(1) == 27:
            print "Esc pressed : exit"
            close_camera()
            break


def test_front_holes_coordinates():
    global nao_motion
    myc4 = Connect4Handler(get_nao_image)
    c4tracker = Connect4Tracker(myc4.model)
    dist = 0.5
    sloped = False
    while True:
        try:
            myc4.detectFrontHoles(dist, sloped, tries=4)
            cv2.imshow("Connect4Handler", myc4.front_hole_detector.getPerspective())
            rvec, tvec = myc4.front_hole_detector.match3DModel(data.CAM_MATRIX, data.CAM_DISTORSION)
            print \
            c4tracker.get_holes_coordinates(rvec, tvec, nao_motion.motion_proxy.getPosition("CameraTop", 0, True))[3]
        except c4.FrontHolesGridNotFoundException:
            pass
        img2 = draw_circles(myc4.img, myc4.circles)
        cv2.imshow("Circles detected", img2)
        cv2.imshow("Original picture", myc4.img)
        if cv2.waitKey(1) == 27:
            print "Esc pressed : exit"
            close_camera()
            break
    return 0


def test_upper_holes_coordinates():
    global nao_motion
    c4tracker = Connect4Tracker(DefaultConnect4Model())
    uhc = upper_hole.UpperHoleDetector(DefaultConnect4Model())
    j = 1

    while True:
        img = get_nao_image(1, res=2)

        # # img = cv2.imread("test_img/img" + str((j % 154) + 1) + ".png")
        # # imgs.append(img.copy())
        markers = detect_markers(img)
        uhc.hamcodes = markers
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (1, 1), 0)
        # gray = cv2.medianBlur(gray, 1)
        edges = cv2.Canny(gray, 195, 200, apertureSize=3)
        edges2 = edges.copy()
        _, cnts, _ = cv2.findContours(edges2, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        rectangles = []
        for cnt in cnts:
            approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True) * 0.01, True)
            # if cv2.contourArea(approx, False) > 40:
            if len(approx) >= 3:
                # print approx
                for i in range(len(approx) - 1):
                    tuple0 = (approx[i][0][0], approx[i][0][1])
                    tuple1 = (approx[i + 1][0][0], approx[i + 1][0][1])
                    # cv2.line(img, tuple0, tuple1, (0, 0, 255), 2)
                tuple0 = (approx[-1][0][0], approx[-1][0][1])
                tuple1 = (approx[0][0][0], approx[0][0][1])
                # cv2.line(img, tuple0, tuple1, (0, 0, 255), 2)
                rect = cv2.minAreaRect(cnt)
                # rectArea = abs(rect[1][0] * rect[1][1])
                box = cv2.boxPoints(rect)
                cntArea = abs(cv2.contourArea(cv2.convexHull(approx), False))
                box = np.int0(box)
                # rectArea = cv2.contourArea(np.array(box), False)
                rectArea = rect[1][0] * rect[1][1]
                if abs(rectArea) <= 1.6 * abs(cntArea):
                    rectangles.append(rect)
                    cv2.drawContours(img, [box], 0, (255, 0, 0), 2)


        for hole in uhc.holes:
            box = cv2.boxPoints(hole)
            box = np.int0(box)
            cv2.drawContours(img, [box], 0, (0, 255, 0), 5)
        # cv2.imshow('contours', img)
        # cv2.imshow('canny', edges)
        if cv2.waitKey(500) == 27:
            print "Esc pressed : exit"
            close_camera()
            # i = 0
            # for img in imgs:
            #     i += 1
            #     cv2.imwrite("test_img/img" + str(i) + ".png", img)
            break
        j += 1
        if len(markers) > 0:
            for m in markers:
                m.draw_contour(img)
                cv2.putText(img, str(m.id), tuple(int(p) for p in m.center),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                print str(m.id) + " " + str(m.contours)
            print
            cv2.imshow('live', img)
            rvec, tvec = uhc.match_3d_model(data.CAM_MATRIX, data.CAM_DISTORSION)
            coords = c4tracker.get_holes_coordinates(rvec, tvec,
                                                     nao_motion.motion_proxy.getPosition("CameraBottom", 0, True))[4]
            coords[2] += 0.1
            print coords.tolist()
            nao_motion.put_hand_at(coords.tolist())
            # time.sleep(5)
        if cv2.waitKey(1) == 27:
            print "Esc pressed : exit"
            close_camera()
            break
        sleep(2)
    return 0


if __name__ == '__main__':
    # test3()
    # test2()
    # test4()
    # testBarCode()
    test_upper_holes_coordinates()
    # test_front_holes_coordinates()
