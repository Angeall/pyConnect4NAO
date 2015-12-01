import time

import cv2
import numpy as np

import connect4 as c4
import src.nao.nao_controller as nao
from src.utils import latex_generator

__author__ = 'Anthony Rouneau'


def get_score(nb_grid_circles, nb_noise_circles):
    return (float(nb_grid_circles)/42.0) - \
           (float(nb_noise_circles)/float((nb_grid_circles+nb_noise_circles)))


def calibration_param2(dist, images, must_latex=True):
    titles = ["\\texttt{param2}", "Grid circles", "Noise circles",
              "Total", "Score"]
    results = []
    counter = 0
    min_dist = int((5/dist)*1.195)
    min_radius = int(5./dist)
    param1 = 60
    max_radius = int(9./dist)
    for img in images:
        table = []
        best_value = -1
        best_score = 0
        # how many pixels for a circle radius on a 320x240px image when standing one meter away
        param2 = 0.
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.medianBlur(gray, 3)
        while param2 < 20:
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
                    best_value = param2
            line = [param2, nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles, len(circles[0]), score]
            table.append(line)
        results.append(best_value)
        param2 += 0.25
        if must_latex:
            latex_generator.generate_longtable(titles, "../../../latex/generated_radius_" + str(counter), table)
        counter += 1
    return results


def calibration_param1(dist, images, must_latex=True):
    titles = ["\\texttt{param1}", "Grid circles", "Noise circles",
              "Total", "Score"]
    results = []
    counter = 0
    min_radius = int(5./dist)
    max_radius = int(9./dist)
    min_dist = int((5./dist)*1.195)
    param2 = 10.5
    for img in images:
        table = []
        best_value = 0
        best_score = 0
        # how many pixels for a circle radius on a 320x240px image when standing one meter away
        param1 = 10
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.medianBlur(gray, 3)
        while param1 < 90:
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, min_dist, param1=param1, param2=param2,
                                       minRadius=min_radius, maxRadius=max_radius)
            if circles is None:
                score = -1000
                nb_of_grid_circles = 0
                circles = [[]]
            else:
                print "Je passe ici"
                # circles = np.uint16(np.around(circles))
                _, nb_of_grid_circles = c4.detect_connect4(circles[0], img)
                if nb_of_grid_circles is None:
                    score = -1000
                    nb_of_grid_circles = 0
                else:
                    score = round(get_score(nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles), 4)
                if score > best_score:
                    best_score = score
                    best_value = param1
            line = [param1, nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles, len(circles[0]), score]
            table.append(line)
            param1 += 1
        results.append(best_value)
        if must_latex:
            latex_generator.generate_longtable(titles, "../../../latex/generated_param1_" + str(counter), table)
        counter += 1
    return results



def calibration_radius_error(dist, images, must_latex=True):
    titles = ["\\texttt{min_radius}", "\\texttt{max_radius}", "\\texttt{min_dist}", "Grid circles", "Noise circles",
              "Total", "Score"]
    results = []
    counter = 0
    factor = 2.3
    for img in images:
        table = []
        best_score = 0.
        # how many pixels for a circle radius on a 320x240px image when standing one meter away
        one_meter_value = 6
        best_upper = one_meter_value
        best_lower = one_meter_value
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.medianBlur(gray, 3)
        while one_meter_value < 8:
            upper_bound = one_meter_value+1
            while upper_bound<factor*one_meter_value:
                lower_bound = one_meter_value-1
                min_dist = round(lower_bound*1.195, 2)
                while lower_bound>one_meter_value/factor:
                    min_radius = int(lower_bound/dist)
                    max_radius = int(upper_bound/dist)
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
                            best_upper = upper_bound
                            best_lower = lower_bound
                    line = [lower_bound, upper_bound, min_dist, nb_of_grid_circles,
                                  len(circles[0]) - nb_of_grid_circles, len(circles[0]), score]
                    table.append(line)
                    print line
                    lower_bound -= 1
                upper_bound += 1
            one_meter_value += 1
        results.append((best_lower, best_upper))
        if must_latex:
            latex_generator.generate_longtable(titles, "../../../latex/generated_radius_" + str(counter), table)
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


if __name__ == "__main__":
    dist = 3
    images = get_images(dist)
    #print calibration_radius_error(dist, images)
    # print calibration_param1(dist, images)
    #print calibration_param2(dist, images)
