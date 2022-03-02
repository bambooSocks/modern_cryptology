import numpy as np


def readTMatrix():
    lines = []
    with open('T6.dat') as f:
        for line in f.readlines():
            lines.append(np.asarray(list(map(float,line.strip().split(',')))))

    return np.asarray(lines)
