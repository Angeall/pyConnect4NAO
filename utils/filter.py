import numpy as np

LINE_CONFIG_MIN_H_DIST = 0
LINE_CONFIG_AVG_H_DIST = 1
LINE_CONFIG_MAX_H_DIST = 2


# def qsort(arr, threshold):
#     if len(arr) <= 1:
#         return arr
#     else:
#         return qsort([x for x in arr[1:] if (
#             (abs(int(x[1]) - int(arr[0][1])) >= threshold) or (int(abs(x[1]) - int(arr[0][1])) >= threshold and x[0] >= arr[0][0]))],
#                      threshold) + [arr[0]] + qsort([x for x in arr[1:] if (
#             (abs(int(x[1]) - int(arr[0][1])) < threshold) or (int(abs(x[1]) - int(arr[0][1])) < threshold and x[0] < arr[0][0]))],
#                                                    threshold)


def circles_matrix(circles, vertical_threshold):
    matrix = []
    if circles is None:
        return matrix
    # (x,y,radius) of the circle are quicksorted by y
    ordered_circles = sorted(circles, key=lambda x: x[1])
    matrix.append([ordered_circles[0]])
    current = ordered_circles[0]
    i = 0
    for circle in ordered_circles[1:]:
        # Is the difference enough to start a new line ?
        if abs(int(circle[1]) - int(current[1])) > vertical_threshold:
            # (x,y,radius) of the circle are quicksorted by x
            matrix[i] = sorted(matrix[i], key=lambda x: x[0])
            i = i + 1
            matrix.append([])
            current = circle
        matrix[i].append(circle)
    return matrix


def point_distance(p1, p2):
    x = abs(int(p2[0]) - int(p1[0]))
    y = abs(int(p2[1]) - int(p1[1]))
    return np.linalg.norm((x, y))


# Returns : (is_correct, line, line_config)
#   line_config : dict
#       LINE_CONFIG_AVG_H_DIST: the average distance between two circles in the line
#       LINE_CONFIG_MIN_H_DIST: the minimum distance between two circles in the line
#       LINE_CONFIG_MAX_H_DIST: the maximum distance between two circles in the line
def correct_line(line, max_h_space=10, min_detected=6, max_missed=1):
    if len(line) < min_detected:
        return False, [], []
    missing = 0
    just_missed = False
    current = line[0]
    line_config = {LINE_CONFIG_AVG_H_DIST: 0,
                   LINE_CONFIG_MIN_H_DIST: 999999999,
                   LINE_CONFIG_MAX_H_DIST: 0}
    total_dist = 0
    i = 1
    _correct_line = [current]
    while i < len(line):
        circle = line[i]
        # if too much was missed return/break the line
        if missing > max_missed:
            break
        expected_dist = max_h_space
        min_dist = current[2] + circle[2]
        # if a circle was just missed
        if just_missed:
            expected_dist = max_h_space * 2
            min_dist = current[2] + circle[2] + ((current[2] + circle[2]) / 2.0)
        _dist = point_distance((circle[0], circle[1]), (current[0], current[1]))
        # if distance between the current and the next is enough
        if _dist < expected_dist:
            # if the circles don't overlap
            if min_dist < _dist:
                _correct_line.append(circle)
                if _dist < line_config[LINE_CONFIG_MIN_H_DIST]:
                    line_config[LINE_CONFIG_MIN_H_DIST] = _dist
                if _dist > line_config[LINE_CONFIG_MAX_H_DIST]:
                    line_config[LINE_CONFIG_MAX_H_DIST] = _dist
                total_dist += _dist
                current = circle
                i = i + 1
            # if it overlaps, problem ! return/break the line
            else:
                break
            just_missed = False
        else:
            # if two consecutive miss : return/break the line
            if just_missed:
                break
            just_missed = True
            missing = missing + 1
    # if not enough detected : continue with next circle
    if len(_correct_line) < min_detected:
        return correct_line(line[1:])
    # else : return the detected line
    line_config[LINE_CONFIG_AVG_H_DIST] = total_dist/len(_correct_line)
    return (True, _correct_line, line_config)


def detect_connect_4_lines(circles, vertical_threshold, max_h_space, min_detected=6, max_missed=1, circle_matrix=None):
    if circles is None:
        return []
    if circle_matrix is None:
        circle_matrix = circles_matrix(circles, vertical_threshold)
    correct_lines = []
    for line in circle_matrix:
        if len(line) < min_detected:
            continue
        (is_correct, ok_line, _) = correct_line(line, max_h_space, min_detected, max_missed)
        if is_correct:
            correct_lines.append(ok_line)
    return correct_lines


def detect_connect_4_grid(circles, vertical_threshold, max_h_space, max_v_space, min_detected=6, max_h_missed=1,
                          max_v_missed=1):
    circle_matrix = circles_matrix(circles, vertical_threshold)
    lines = detect_connect_4_lines(circles, vertical_threshold, max_h_space, min_detected, max_h_missed,
                                   circle_matrix=circle_matrix)
    if len(lines) < 6 - max_v_missed:
        return None
    grid = [[(), (), (), (), (), (), ()],
            [(), (), (), (), (), (), ()],
            [(), (), (), (), (), (), ()],
            [(), (), (), (), (), (), ()],
            [(), (), (), (), (), (), ()],
            [(), (), (), (), (), (), ()]]
    # TODO: Check if all line complete : Yes: check if all aligned -- No: Try to complete lines
    # TODO : Complete missing row in line : threshold = avg_dist-min_dist try to find hole at known +/- min_dist
    # TODO : Complete missing line : check known line => if potential line below/above it => add it
