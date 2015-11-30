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


def calibration_radius_error(dist, images, must_latex=True):
    titles = ["\\texttt{min_radius}", "\\texttt{max_radius}", "\\texttt{min_dist}", "Grid circles", "Noise circles",
              "Total", "Score"]
    results = []
    counter = 0
    for img in images:
        table = []
        best_score = 0.
        # how many pixels for a circle radius on a 320x240px image when standing one meter away
        one_meter_value = 6
        best_upper = one_meter_value
        best_lower = one_meter_value
        lower_bound = one_meter_value-1
        upper_bound = one_meter_value+1
        min_dist = round(lower_bound*1.195, 2)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.medianBlur(gray, 3)
        while upper_bound<3*one_meter_value:
            lower_bound = one_meter_value-1
            while lower_bound>one_meter_value/3.0:
                circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, min_dist, param1=60, param2=10.5,
                                           minRadius=int(lower_bound), maxRadius=upper_bound)
                if circles is None:
                    score = "-1000"
                    nb_of_grid_circles = 0
                    circles = [[]]
                else:
                    # circles = np.uint16(np.around(circles))
                    _, nb_of_grid_circles = c4.detect_connect4(circles[0], img)
                    if nb_of_grid_circles is None:
                        score = "-1000"
                    else:
                        score = round(get_score(nb_of_grid_circles, len(circles[0]) - nb_of_grid_circles), 2)
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
        results.append((best_lower, best_upper))
        if must_latex:
            latex_generator.generate_longtable(titles, "radius_" + str(counter), table)
        counter += 1
        print
    return results


def get_images():
    nao_c = nao.NAOController(nao.IP, nao.PORT)
    nao_c.unsubscribe_all_cameras()
    nao_c.connect_to_camera(res=1, fps=10, camera_num=0)
    images = []
    start = time.time()
    current = time.time()
    while current-start < 10:
        images.append(nao_c.get_image_from_camera())
        current = time.time()
    return images


if __name__ == "__main__":
    dist = 1.
    images = get_images()
    calibration_radius_error(dist, images)
