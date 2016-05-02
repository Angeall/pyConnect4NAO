import numpy as np

__author__ = 'Anthony Rouneau'

# IP = "127.0.0.1"
# IP = "192.168.208.42"
IP = "169.254.254.250"
# IP = "192.168.2.24"
# PORT = 35271
PORT = 9559

# TODO : Make the CAM_MATRIX resolution independant

CAM_MATRIX = np.matrix([[284.633411,    0.,           152.559524],
                        [0.,            283.623835,   109.060664],
                        [0.,              0.,         1.]])

CAM_DISTORSION = np.matrix([[-1.11113889e-02,   2.39798893e-05,  -4.37419724e-04,   1.39974687e-03,  -1.33569168e-08]])

# CAM_MATRIX = np.matrix([[295.89693416,    0.,          180.02883199],
#                         [0.,            235.00611377,   90.64409278],
#                         [0.,              0.,            1.]])
# CAM_DISTORSION = np.matrix([[0.1363378,  -1.97377046,  0.01807662,  0.00988139,  4.50583262]])