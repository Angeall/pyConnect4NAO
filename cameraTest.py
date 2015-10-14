import numpy as np
import naoqi
import nao.nao_controller as naoc
import cv2
__author__ = 'Angeall'
robot_ip = "192.168.2.24"
port = 9559


def nothing(x):
    pass


def test():
    nao_c = naoc.NAOController(robot_ip, port)
    ret = nao_c.connect_to_camera()

    # cap = cv2.VideoCapture(0)
    if ret < 0:
        print "Could not open camera"
        return -1
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
    while True:
        img = nao_c.get_image_from_camera()
        # if not hasRead:
        #     print "Image not readable"
        #     break
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,1,5,
                            param1=50,param2=10,minRadius=5,maxRadius=8)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                # draw the outer circle
                cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
                # draw the center of the circle
                cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)

        cv2.imshow("Original Image", img)

        if cv2.waitKey(1) == 27:
            print "Esc pressed : exit"
            nao_c.disconnect_from_camera()
            break
    return 0


if __name__ == '__main__':
    test()