import generic.grid_detection as grid
import generic.grid_perspective as perspective
import cv2
__author__ = 'Angeall'

connect4_img_name = "Connect4.png"
connect4_img = cv2.imread(connect4_img_name)
reference_mapping = {}


def detect_connect4(keypoints, scene_img):
    global reference_mapping
    if len(reference_mapping) == 0:
        reference_mapping = grid.map_virtual_circle_grid()
    (found, mapping, nb_of_grid_circles) = grid.detect_grid(keypoints)
    if not found:
        return None, None
    mapping = grid.index_mapping_into_pixel_mapping(mapping, keypoints)
    return perspective.get_perspective(reference_mapping, mapping, connect4_img, scene_img), nb_of_grid_circles



