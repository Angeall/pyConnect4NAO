import time

import cv2
import numpy as np

import connect4 as c4
import src.nao.nao_controller as nao
from src.utils import latex_generator

__author__ = 'Anthony Rouneau'


def get_score(nb_grid_circles, nb_noise_circles):
    total_circles = float((nb_grid_circles+nb_noise_circles))
    if total_circles == 0:
        return -2
    return (float(nb_grid_circles)/42.0) - \
           (float(nb_noise_circles)/total_circles)


def calibration_param2(dist, images, must_latex=True):
    titles = ["\\texttt{param2}", "Grid circles", "Noise circles",
              "Total", "Score"]
    results = []
    counter = 0
    max_radius = estimate_maxradius(dist)
    min_radius = estimate_minradius(dist)
    min_dist = int(min_radius*1.195)
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
                # circles = np.uint16(np.around(circles))
                _, nb_of_grid_circles = c4.detect_connect4(circles[0], img)
                if nb_of_grid_circles is None:
                    nb_of_grid_circles = 0
            score = round(get_score(nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles), 4)
            if score > best_score:
                best_score = score
                best_value = [param2]
            elif abs(score-best_score)<0.00001:
                best_value.append(param2)
            line = [param2, nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles, len(circles[0]), score]
            table.append(line)
            param2 += 0.25
        results.append(best_value)
        print "radius : image " + str(counter) + " finished"
        if must_latex:
            latex_generator.generate_longtable(titles, "../../../latex/generated_radius_" +
                                               str(dist) + "_" + str(counter), table)
        counter += 1
    return results


def calibration_param1(dist, images, must_latex=True):
    titles = ["\\texttt{param1}", "Grid circles", "Noise circles",
              "Total", "Score"]
    results = []
    counter = 0
    min_radius = estimate_minradius(dist)
    max_radius = estimate_maxradius(dist)
    min_dist = int(min_radius*1.195)
    param2 = 10.5
    for img in images:
        table = []
        best_value = []
        best_score = -1000
        # how many pixels for a circle radius on a 320x240px image when standing one meter away
        param1 = 30
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.medianBlur(gray, 3)
        while param1 < 200:
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, min_dist, param1=param1, param2=param2,
                                       minRadius=min_radius, maxRadius=max_radius)
            if circles is None:
                score = -1000
                nb_of_grid_circles = 0
                circles = [[]]
            else:
                # circles = np.uint16(np.around(circles))
                _, nb_of_grid_circles = c4.detect_connect4(circles[0], img)
                if nb_of_grid_circles is None:
                    score = -1000
                    nb_of_grid_circles = 0
                else:
                    score = round(get_score(nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles), 4)
                if score > best_score:
                    best_score = score
                    best_value = [param1]
                elif abs(score-best_score)<0.00001:
                    best_value.append(param1)
            line = [param1, nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles, len(circles[0]), score]
            table.append(line)
            param1 += 1
        results.append(best_value)
        print "param1 : image " + str(counter) + " finished"
        if must_latex:
            latex_generator.generate_longtable(titles, "../../../latex/generated_param1_" +
                                               str(dist) + "_" + str(counter), table)
        counter += 1
    return results


def estimate_minradius(dist):
    return int(4.4143*(dist**(-1.1446)))


def estimate_maxradius(dist):
    return int(round(8.5468*(dist**(-0.7126))))


def calibration_radius_error(dist, images, must_latex=True):
    titles = ["\\texttt{minRadius}", "\\texttt{maxRadius}", "\\texttt{minDist}", "Grid circles", "Noise circles",
              "Total", "Score"]
    results = []
    counter = 0
    factor = 3.0*dist
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
            dist_value = int(round(one_meter_value/dist))
            upper_bound = (dist_value+1)
            while upper_bound<(factor*one_meter_value)/dist:
                lower_bound = (dist_value-1)
                while lower_bound>(one_meter_value/factor)/dist:
                    min_radius = int(lower_bound)
                    max_radius = int(upper_bound)
                    min_dist = round(lower_bound*1.125, 2)
                    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, min_dist, param1=48, param2=10.5,
                                               minRadius=min_radius, maxRadius=max_radius)
                    if circles is None:
                        score = -1000
                        nb_of_grid_circles = 0
                        circles = [[]]
                    else:
                        # circles = np.uint16(np.around(circles))
                        _, nb_of_grid_circles = c4.detect_connect4(circles[0], img)
                        if nb_of_grid_circles is None:
                            score = -1000
                            nb_of_grid_circles = 0
                        else:
                            score = round(get_score(nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles), 4)
                        if score > best_score:
                            best_score = score
                            best_value = [(min_radius, max_radius)]
                        elif abs(score-best_score)<0.00001:
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
            latex_generator.generate_longtable(titles, "../../../latex/generated_radius_" +
                                               str(dist) + "_" + str(counter), table)
        counter += 1
    return results


def get_images(dist):
    nao_c = nao.NAOController(nao.IP, nao.PORT)
    nao_c.unsubscribe_all_cameras()
    nao_c.connect_to_camera(res=1, fps=5, camera_num=0)
    images = []
    max_time = 15
    start = time.time()
    current = time.time()
    while current-start < max_time:
        images.append(nao_c.get_image_from_camera())
        current = time.time()
    for i, img in enumerate(images):
        cv2.imwrite("../../../latex/img/" + str(dist) + "m/img_" + str(i) + ".png", img)
    return images


def evaluate(best_values, param, dist):
    scores = {}
    titles = ["\\texttt{param" + param + "}","Occurrences"]
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
    latex_generator.generate_longtable(titles, "../../../latex/value/" + str(param) + "_" + str(dist), table)
    return best_values


def load_images(dist):
    images = []
    for i in range(40):
        filename = "../../../latex/img/" + str(dist) + "m/img_" + str(i) + ".png"
        images.append(cv2.imread(filename))
    return images


if __name__ == "__main__":
    dists = [0.4, 0.5, 1, 1.5, 2, 2.5, 3]
    # images = get_images(dist)
    for dist in dists:
        print "-"*20 + str(dist) + "-"*20
        images = load_images(dist)
        #print evaluate(calibration_radius_error(dist, images), "(minRadius, maxRadius)", dist)
        print evaluate(calibration_param1(dist, images), "param1", dist)
        #print evaluate(calibration_param2(dist, images), "param2", dist)
