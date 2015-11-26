import generic.grid_detection as grid
import generic.grid_perspective as perspective
import cv2
__author__ = 'Angeall'

connect4_img_name = "Connect4.png"
connect4_img = cv2.imread(connect4_img_name)


def detect_connect4(keypoints, scene_img):
    connect4_mapping = grid.map_virtual_circle_grid()
    (found, mapping) = grid.detect_grid(keypoints)
    if not found:
        return None
    mapping = grid.index_mapping_into_pixel_mapping(mapping, keypoints)
    return perspective.get_perspective(connect4_mapping, mapping, connect4_img, scene_img)

