import cv2
import numpy as np
__author__ = 'Angeall'


def mapping_homography(object_mapping, scene_mapping):
    """
    Find a homography between an object and a scene, represented by two mappings with similar keys.
    Warning : keys of scene_mapping must be included in the keys of object_mapping.
    :param object_mapping: The mapping between relative coordinates and pixel coordinates of the searched object.
    :type object_mapping: dict
    :param scene_mapping: The mapping between relative coordinates and pixel coordinates of the object in the scene.
    :type scene_mapping: dict
    :return: The homography, computed by OpenCV, between the object and the scene
    :rtype: np.matrix
    """
    obj = []
    scene = []
    for key in scene_mapping.keys():
        obj.append(object_mapping[key])
        scene.append(scene_mapping[key])
    obj = np.array(obj)
    scene = np.array(scene)
    return cv2.findHomography(obj, scene, cv2.RANSAC)[0]


def get_object_in_scene(homography, object_img, scene_img):
    """
    Use OpenCV's warpPerspective to isolate the object in the scene.
    :param homography: The homography, result of mapping_homography
    :type homography: np.matrix
    :param object_img: The image representing the object to find in the scene
    :type object_img: np.matrix
    :param scene_img: The scene in which you want to find the object
    :type scene_img: np.matrix
    :return: The scene, reshaped so only the object in the scene is visible, formatted as object_img
    """
    rows, cols, _ = object_img.shape
    return cv2.warpPerspective(scene_img, homography, (cols, rows), flags=cv2.WARP_INVERSE_MAP)


def get_perspective(object_mapping, scene_mapping, object_img, scene_img):
    """
    Get the image of a specific object in a scene
    :param object_mapping: The mapping between relative coordinates and pixel coordinates of the searched object.
    :type object_mapping: dict
    :param scene_mapping: The mapping between relative coordinates and pixel coordinates of the object in the scene.
    :type scene_mapping: dict
    :param object_img: The image representing the object to find in the scene
    :type object_img: np.matrix
    :param scene_img: The scene in which you want to find the object
    :type scene_img: np.matrix
    :return: The image of the object in the scene
    :rtype: np.matrix
    """
    homography = mapping_homography(object_mapping, scene_mapping)
    return get_object_in_scene(homography, object_img, scene_img)

