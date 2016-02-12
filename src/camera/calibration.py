import time

import cv2

import nao.nao_controller as nao
from connect4 import frontholedetector as c4
from connect4.connect4 import *
from utils import latex_generator

__author__ = 'Anthony Rouneau'

robot_ip = "192.168.2.16"
port = 9559
detector = c4.FrontHoleDetector()
connect4 = Connect4()
nao_c = None


def clean():
    global nao_c
    if nao_c is not None:
        nao_c.clean()


def get_nao_image(camera_num=0):
    global nao_c
    if nao_c is None:
        nao_c = nao.NAOController(robot_ip, port)
        clean()
        ret = nao_c.connectToCamera(res=1, fps=30, camera_num=camera_num)
        if ret < 0:
            print "Could not open camera"
            return None
    return nao_c.getImageFromCamera()


def get_camera_information():
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    objp = np.zeros((6*7,3), np.float32)
    objp[:, :2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

    objpoints = []  # 3d point
    imgpoints = []  # 2d point

    finished = False

    while not finished:
        img = get_nao_image()
        if img is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (7, 6), None)

            # If the chessboard is found, add object points, image points
            if ret:
                objpoints.append(objp)

                cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                imgpoints.append(corners)

                # Draw and display the corners
                cv2.drawChessboardCorners(img, (7, 6), corners, ret)
                cv2.imshow('img', img)
                if cv2.waitKey(2500) == 27:  # ESC pressed ?
                    finished = True
                if not finished:
                    # We wait 2 seconds so the operator can move the chessboard
                    time.sleep(2)

    cv2.destroyAllWindows()
    ret, mtx, disto, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
    return mtx, disto


def get_f_score(nb_grid_circles, nb_noise_circles):
    total_circles = float((nb_grid_circles + nb_noise_circles))
    if total_circles == 0 or nb_grid_circles == 0:
        return 0
    recall = float(nb_grid_circles) / total_circles
    precision = float(nb_grid_circles) / 42.0
    return (2 * precision * recall) / (precision + recall)


def calibration_param2(dist, images, must_latex=True):
    global detector, connect4
    titles = ["\\texttt{param2}", "Grid circles", "Noise circles",
              "Total", "Score"]
    results = []
    counter = 0
    max_radius = connect4.estimateMaxRadius(dist)
    min_radius = connect4.estimateMinRadius(dist)
    max_error = connect4.computeMaxPixelError(min_radius)
    min_dist = int(min_radius * 1.195)
    param1 = 60

    for img in images:
        table = []
        best_value = []
        best_score = -1000
        # how many pixels for a circle radius on a 320x240px image when standing one meter away
        param2 = 5.
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.medianBlur(gray, 3)
        while param2 < 17:
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, min_dist, param1=param1, param2=param2,
                                       minRadius=min_radius, maxRadius=max_radius)
            if circles is None:
                nb_of_grid_circles = 0
                circles = [[]]
            else:
                try:
                    detector.runDetection(circles[0], pixel_error_margin=max_error)
                    nb_of_grid_circles = len(detector.relativeCoordinates)
                except c4.CircleGridNotFoundException:
                    nb_of_grid_circles = 0
            score = round(get_f_score(nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles), 4)
            if score > best_score:
                best_score = score
                best_value = [param2]
            elif abs(score - best_score) < 0.00001:
                best_value.append(param2)
            line = [param2, nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles, len(circles[0]), score]
            table.append(line)
            param2 += 0.25
        results.append(best_value)
        print "radius : image " + str(counter) + " finished"
        if must_latex:
            latex_generator.generate_longtable(titles, "../../latex/generated_radius_" +
                                               str(dist) + "_" + str(counter), table)
        counter += 1
    return results


def plotting_param2(dist, images):
    global detector, connect4
    results = {}
    counter = 0
    max_radius = connect4.estimateMaxRadius(dist)
    min_radius = connect4.estimateMinRadius(dist)
    max_error = connect4.computeMaxPixelError(min_radius)
    min_dist = int(min_radius * 1.195)
    param1 = 60

    for img in images:
        # how many pixels for a circle radius on a 320x240px image when standing one meter away
        param2 = 5.
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.medianBlur(gray, 3)
        while param2 < 17:
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, min_dist, param1=param1, param2=param2,
                                       minRadius=min_radius, maxRadius=max_radius)
            if circles is None:
                nb_of_grid_circles = 0
                circles = [[]]
                score = 0
            else:
                # circles = np.uint16(np.around(circles))
                try:
                    detector.runDetection(circles[0], pixel_error_margin=max_error)
                    nb_of_grid_circles = len(detector.relativeCoordinates)
                    score = round(get_f_score(nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles), 4)
                except c4.CircleGridNotFoundException:
                    score = 0
                    nb_of_grid_circles = 0

            param2 += 0.25
            key = str(round(param2, 2))
            if results.has_key(key):
                results[key].append(score)
            else:
                results[key] = [score]
        print "param2 : image " + str(counter) + " finished"
        counter += 1
    return results


def calibration_param1(dist, images, must_latex=True):
    global detector, connect4
    titles = ["\\texttt{param1}", "Grid circles", "Noise circles",
              "Total", "Score"]
    results = []
    counter = 0
    min_radius = connect4.estimateMinRadius(dist)
    max_radius = connect4.estimateMaxRadius(dist)
    max_error = connect4.computeMaxPixelError(min_radius)
    min_dist = int(min_radius * 1.195)
    param2 = 10.5
    for img in images:
        table = []
        best_value = []
        best_score = 0
        # how many pixels for a circle radius on a 320x240px image when standing one meter away
        param1 = 30
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.medianBlur(gray, 3)
        while param1 < 200:
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, min_dist, param1=param1, param2=param2,
                                       minRadius=min_radius, maxRadius=max_radius)
            if circles is None:
                score = 0
                nb_of_grid_circles = 0
                circles = [[]]
            else:
                try:
                    detector.runDetection(circles[0], pixel_error_margin=max_error)
                    nb_of_grid_circles = len(detector.relativeCoordinates)
                    score = round(get_f_score(nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles), 4)
                except c4.CircleGridNotFoundException:
                    score = 0
                    nb_of_grid_circles = 0
                if score > best_score:
                    best_score = score
                    best_value = [param1]
                elif abs(score - best_score) < 0.00001:
                    best_value.append(param1)
            line = [param1, nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles, len(circles[0]), score]
            table.append(line)
            param1 += 1
        results.append(best_value)
        print "param1 : image " + str(counter) + " finished"
        if must_latex:
            latex_generator.generate_longtable(titles, "../../latex/generated_param1_" +
                                               str(dist) + "_" + str(counter), table)
        counter += 1
    return results


def plotting_param1(dist, images):
    global detector, connect4
    results = {}
    counter = 0
    min_radius = connect4.estimateMinRadius(dist)
    max_radius = connect4.estimateMaxRadius(dist)
    max_error = connect4.computeMaxPixelError(min_radius)
    min_dist = int(min_radius * 1.195)
    param2 = 10.5
    for img in images:
        best_score = -1
        # how many pixels for a circle radius on a 320x240px image when standing one meter away
        param1 = 30
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.medianBlur(gray, 3)
        while param1 < 200:
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, min_dist, param1=param1, param2=param2,
                                       minRadius=min_radius, maxRadius=max_radius)
            if circles is None:
                score = 0
                nb_of_grid_circles = 0
                circles = [[]]
            else:
                try:
                    detector.runDetection(circles[0], pixel_error_margin=max_error)
                    nb_of_grid_circles = len(detector.relativeCoordinates)
                    score = round(get_f_score(nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles), 4)
                except c4.CircleGridNotFoundException:
                    score = 0
                    nb_of_grid_circles = 0
                else:
                    score = round(get_f_score(nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles), 4)

            param1 += 1
            if results.has_key(param1):
                results[param1].append(score)
            else:
                results[param1] = [score]
        print "param1 : image " + str(counter) + " finished"
        counter += 1
    return results


def calibration_radius_error(dist, images, must_latex=True):
    global detector, connect4
    titles = ["\\texttt{minRadius}", "\\texttt{maxRadius}", "\\texttt{minDist}", "Grid circles", "Noise circles",
              "Total", "Score"]
    results = []
    counter = 0
    factor = 3.0 * dist
    for img in images:
        table = []
        best_score = -1000
        # how many pixels for a circle radius on a 320x240px image when standing one meter away
        one_meter_value = 6
        best_value = []
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.medianBlur(gray, 3)
        while one_meter_value < 8:
            dist_value = int(round(one_meter_value / dist))
            upper_bound = (dist_value + 1)
            while upper_bound < (factor * one_meter_value) / dist:
                lower_bound = (dist_value - 1)
                while lower_bound > (one_meter_value / factor) / dist:
                    min_radius = int(lower_bound)
                    max_radius = int(upper_bound)
                    max_error = connect4.computeMaxPixelError(min_radius)
                    min_dist = round(lower_bound * 1.125, 2)
                    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, min_dist, param1=48, param2=10.5,
                                               minRadius=min_radius, maxRadius=max_radius)
                    if circles is None:
                        score = 0
                        nb_of_grid_circles = 0
                        circles = [[]]
                    else:
                        # circles = np.uint16(np.around(circles))
                        try:
                            detector.runDetection(circles[0], pixel_error_margin=max_error)
                            nb_of_grid_circles = len(detector.relativeCoordinates)
                            score = round(get_f_score(nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles), 4)
                        except c4.CircleGridNotFoundException:
                            score = 0
                            nb_of_grid_circles = 0
                        if score > best_score:
                            best_score = score
                            best_value = [(min_radius, max_radius)]
                        elif abs(score - best_score) < 0.00001:
                            best_value.append((min_radius, max_radius))
                    line = [lower_bound, upper_bound, min_dist, nb_of_grid_circles,
                            len(circles[0]) - nb_of_grid_circles, len(circles[0]), score]
                    table.append(line)
                    lower_bound -= 1
                upper_bound += 1
            one_meter_value += 1
        print "radius : image " + str(counter) + " finished"
        results.append(best_value)
        if must_latex:
            latex_generator.generate_longtable(titles, "../../latex/generated_radius_" +
                                               str(dist) + "_" + str(counter), table)
        counter += 1
    return results


def get_images(dist):
    nao_c = nao.NAOController(nao.IP, nao.PORT)
    nao_c.unsubscribeAllCameras()
    nao_c.connectToCamera(res=1, fps=5, camera_num=0)
    images = []
    max_time = 15
    start = time.time()
    current = time.time()
    while current - start < max_time:
        images.append(nao_c.getImageFromCamera())
        current = time.time()
    for i, img in enumerate(images):
        cv2.imwrite("../../../latex/img/" + str(dist) + "m/img_" + str(i) + ".png", img)
    return images


def evaluate(best_values, param, dist):
    scores = {}
    titles = ["\\texttt{param" + param + "}", "Occurrences"]
    table = []
    for iteration in best_values:
        for value in iteration:
            if scores.has_key(value):
                scores[value] += 1
            else:
                scores[value] = 1
    for value in scores:
        line = [value, scores[value]]
        table.append(line)
    latex_generator.generate_longtable(titles, "../../latex/value/" + str(param) + "_" + str(dist), table)
    return best_values


def load_images(dist):
    images = []
    for i in range(40):
        filename = "../../latex/img/" + str(dist) + "m/img_" + str(i) + ".png"
        images.append(cv2.imread(filename))
    return images


def prepare_plot(scores, param_name):
    data_file = open("../../plot/" + param_name + ".dat", 'w')
    big_dict = {}
    for dico in scores:
        for key in dico:
            if big_dict.has_key(key):
                big_dict[key].extend(dico[key])
            else:
                big_dict[key] = dico[key]
    data = "#" + param_name + " mean var\n"
    for key in big_dict:
        mean = round(np.mean(big_dict[key]), 4)
        var = round(np.var(big_dict[key]), 4)
        data += str(key) + " " + str(mean) + " " + str(var) + '\n'
    data_file.write(data)
    data_file.close()


if __name__ == "__main__":
    # dists = [0.4, 0.5, 1, 1.5, 2, 2.5, 3]
    # images = get_images(dist)
    # scores2 = []
    # scores1 = []
    # for dist in dists:
        # print "-" * 20 + str(dist) + "-" * 20
        # images = load_images(dist)
        # print evaluate(calibration_radius_error(dist, images), "(minRadius, maxRadius)", dist)
        # print evaluate(calibration_param1(dist, images), "param1", dist)
        # print evaluate(calibration_param2(dist, images), "param2", dist)
        # scores1.append(plotting_param1(dist, images))
        # scores2.append(plotting_param2(dist, images))
    # prepare_plot(scores1, "param1")
    # prepare_plot(scores2, "param2")
    camera_file = open("../../values/" + "camera_information" + ".dat", 'w')
    cam_mat, cam_disto = get_camera_information()
    camera_file.write(str(cam_mat) + "\n\n" + str(cam_disto))


