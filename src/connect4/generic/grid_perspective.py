import cv2

__author__ = 'Angeall'


def mapping_homography(object_mapping, scene_mapping):
    """
    Find a homography between an object and a scene, represented by two mappings with similar keys.
    Warning : keys of scene_mapping must be included in the keys of object_mapping.
    :param object_mapping:
    :type object_mapping: dict
    :param scene_mapping:
    :type scene_mapping: dict
    :return: The homography, computed by OpenCV, between the object and the scene
    """
    obj = []
    scene = []
    for key in scene_mapping.keys():
        obj.append(object_mapping[key])
        scene.append(scene_mapping[key])
    return cv2.findHomography(obj, scene, cv2.RANSAC)


def get_object_in_scene(homography, object_img, scene_img):
    rows, cols, _ = object_img.shape
    return cv2.warpPerspective(scene_img, homography, (cols, rows))
    # TODO : tests

