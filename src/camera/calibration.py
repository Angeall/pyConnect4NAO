import time

from connect4.connect4handler import *
from connect4.detector import front_holes as c4
from nao import data
from nao.controller.motion import MotionController
from nao.controller.video import VideoController
from utils import latex_generator

__author__ = 'Anthony Rouneau'


def get_nao_image(camera_num=0):
    global nao_video, nao_motion
    if nao_video is None:
        nao_video = VideoController()
        nao_motion = MotionController()
        # clean()
        ret = nao_video.connectToCamera(res=2, fps=30, camera_num=camera_num)
        if ret < 0:
            print "Could not open camera"
            return None
    return nao_video.getImageFromCamera()

connect4 = Connect4Handler(get_nao_image)
# connect4 = None
connect4_model = connect4.model
# connect4_model = None
detector = c4.FrontHolesDetector(connect4_model)
nao_video = None
nao_motion = None


def get_camera_information():
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    v_margin = 0.024
    h_margin = 0.0135
    square_length = 0.025

    colors_boundaries = [
        (np.array([0, 0, 0]), np.array([255, 80, 80])),
        (np.array([0, 0, 0]), np.array([80, 255, 120])),
        (np.array([0, 0, 0]), np.array([120, 80, 255]))]
    color_names = ["Blue", "Green", "Red"]

    # noinspection PyPep8
    objp = np.zeros((6 * 9, 3), np.float32)
    objp[:, 1:3][:, ::-1] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)
    objp[:, 2] *= -1  # So it's left to right
    objp[:, 2] += 8
    objp *= square_length
    np.add(objp, np.array([0, v_margin, h_margin]))

    objp2 = np.zeros((6 * 9, 3), np.float32)
    objp2[:, ::2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)
    objp2 *= square_length
    np.add(objp2, np.array([h_margin, 0, v_margin]))

    objp3 = np.zeros((6 * 9, 3), np.float32)
    objp3[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)
    objp3 *= square_length
    np.add(objp3, np.array([h_margin, h_margin, 0]))

    objp = np.append(np.append(objp, objp2, axis=0), objp3, axis=0)

    objpoints = []  # 3d point
    imgpoints = []  # 2d point

    finished = False
    gray = None
    # ctr = -1
    while not finished:
        img = get_nao_image()
        if img is not None:
            chessboards_not_found = False
            chessboards_corners = [None, None, None]
            # ctr += 1
            # cv2.imwrite("../../values/calibration" + "_" + str(ctr) + ".png", img)
            i = 0
            img2 = img.copy()
            for (lower, upper) in colors_boundaries:
                mask = cv2.inRange(img2, lower, upper)
                output = cv2.bitwise_and(img2, img2, mask=mask)
                gray2 = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
                gray = cv2.bitwise_not(gray2, gray2)
                color_name = color_names[i]
                i += 1
                # Find the chess board corners
                ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)
                cv2.imshow(color_name, gray)
                cv2.waitKey(500)
                # If one of the chessboards is not detected, we break
                if not ret:
                    chessboards_not_found = True
                    print "NOT FOUND", color_name
                    break
                # If the chessboard is found, add object points, image points
                else:
                    chessboards_corners[i - 1] = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                    # cv2.putText(img, str(color_name), tuple(int(p) for p in corners[0]),
                    #             cv2.FONT_HERSHEY_SIMPLEX, 1, tuple(colors_boundaries[i - 1][1]), 3)
                    # Draw and display the corners
                    cv2.drawChessboardCorners(img, (9, 6), corners, ret)

            # If three chessboards have been detected
            if not chessboards_not_found:
                if geom.point_distance(chessboards_corners[0][0][0], chessboards_corners[1][0][0]) \
                        > geom.point_distance(chessboards_corners[0][45][0], chessboards_corners[1][0][0]):
                    chessboards_corners[0] = chessboards_corners[0][::-1]
                if geom.point_distance(chessboards_corners[2][0][0], chessboards_corners[1][0][0]) \
                        > geom.point_distance(chessboards_corners[2][45][0], chessboards_corners[1][0][0]):
                    chessboards_corners[2] = chessboards_corners[2][::-1]
                if geom.point_distance(chessboards_corners[1][0][0], chessboards_corners[2][0][0]) \
                        > geom.point_distance(chessboards_corners[1][45][0], chessboards_corners[2][0][0]):
                    chessboards_corners[1] = chessboards_corners[1][::-1]
                chessboards_corners = np.append(np.append(chessboards_corners[0], chessboards_corners[1], axis=0),
                                                chessboards_corners[2], axis=0)
                print "3D Model"
                print objp
                print
                print "Found Chessboard"
                print chessboards_corners

                objpoints.append(objp)
                imgpoints.append(chessboards_corners)
            cv2.imshow('img', img)
            if cv2.waitKey(1) == 27:  # ESC pressed ?
                finished = True
            if not finished:
                # We wait 2 seconds so the operator can move the chessboard
                time.sleep(2)

    cv2.destroyAllWindows()
    init_intrinsic = data.CAM_MATRIX
    dist = data.CAM_DISTORSION
    ret, mtx, disto, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], init_intrinsic, dist,
                                                        flags=cv2.CALIB_USE_INTRINSIC_GUESS)
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
            if key in results:
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
            if param1 in results:
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
    global nao_video
    nao_video = VideoController()
    nao_video.unsubscribeAllCameras()
    nao_video.connectToCamera(res=1, fps=5, camera_num=0)
    images = []
    max_time = 15
    start = time.time()
    current = time.time()
    while current - start < max_time:
        images.append(nao_video.getImageFromCamera())
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
            if value in scores:
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
            if key in big_dict:
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
    # image = get_images(dist)
    # scores2 = []
    # scores1 = []
    # for dist in dists:
    # print "-" * 20 + str(dist) + "-" * 20
    # image = load_images(dist)
    # print evaluate(calibration_radius_error(dist, image), "(minRadius, maxRadius)", dist)
    # print evaluate(calibration_param1(dist, image), "param1", dist)
    # print evaluate(calibration_param2(dist, image), "param2", dist)
    # scores1.append(plotting_param1(dist, image))
    # scores2.append(plotting_param2(dist, image))
    # prepare_plot(scores1, "param1")
    # prepare_plot(scores2, "param2")
    camera_file = open("../../values/" + "camera_information" + ".dat", 'w')
    cam_mat, cam_disto = get_camera_information()
    camera_file.write(str(cam_mat) + "\n\n" + str(cam_disto))
    camera_file.close()
