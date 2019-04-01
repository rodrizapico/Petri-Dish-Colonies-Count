#!/usr/bin/env python

'''
This sample demonstrates Canny edge detection.
Usage:
  edge.py [<video source>]
  Trackbars control edge thresholds.
'''

import sys
import cv2 as cv
import numpy as np

def main(argv):

    def nothing(*arg):
        pass

    cv.namedWindow('edge')
    cv.createTrackbar('thrs1', 'edge', 2000, 5000, nothing)
    cv.createTrackbar('thrs2', 'edge', 4000, 5000, nothing)

    ## [load]
    default_file =  "./data/sample5.png" # sample#.jpg , smarties.png
    filename = argv[0] if len(argv) > 0 else default_file

    img = cv.imread(filename, cv.IMREAD_COLOR)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    while True:
        thrs1 = cv.getTrackbarPos('thrs1', 'edge')
        thrs2 = cv.getTrackbarPos('thrs2', 'edge')

        edge = cv.Canny(gray, thrs1, thrs2, apertureSize=5)
        vis = img.copy()
        vis = np.uint8(vis/2.)
        vis[edge != 0] = (0, 255, 0)
        cv.imshow('edge', vis)
        ch = cv.waitKey(5)
        if ch == 27:
            break
    return 0

if __name__ == "__main__":
    main(sys.argv[1:])    