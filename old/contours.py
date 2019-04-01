#!/usr/bin/env python

'''
This program illustrates the use of findContours and drawContours.
The original image is put up along with the image of drawn contours.
Usage:
    contours.py
A trackbar is put up which controls the contour level from -3 to 3
'''

# Python 2/3 compatibility
from __future__ import print_function
import sys
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

import numpy as np
import cv2 as cv

import scipy
import scipy.stats

import matplotlib.pyplot as plt

if __name__ == '__main__':
    print(__doc__)

    default_file =  "./data/sample6.jpg" # sample#.jpg , smarties.png
    filename = sys.argv[1] if len(sys.argv) > 1 else default_file

    img = cv.imread(filename, cv.IMREAD_COLOR)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    levels = 4
    thrs1 = 2000
    thrs2 = 4000

    def updateLevels(lvl):
        global levels
        levels = lvl - 3
        update()
    def updateThrs1(t1):
        global thrs1
        thrs1 = t1
        update()
    def updateThrs2(t2):
        global thrs2
        thrs2 = t2
        update()

    def analyzeContours(contours):

        measuredContours = []
        areaVariations = []
        eccentricities = []

        for contour in contours:
            variation = np.Inf
            eccentricity = np.Inf
            if len(contour) >= 5:
                (x, y), (ma, MA), angle = cv.fitEllipse(contour)
                a = MA/2
                b = ma/2

                cArea = cv.contourArea(contour)
                ellipseArea = a * b * np.pi
                variation = ellipseArea - cArea

                eccentricity = np.sqrt(1 - np.power(b,2)/np.power(a,2))
                eccentricity = np.round(eccentricity, 2)

                #if variation < 40:
                areaVariations.append(variation)
                #if eccentricity < 0.5:
                eccentricities.append(eccentricity)                

            measuredContour = {
                'contour': contour,
                'areaVariation': variation,
                'ellipseEccentricity': eccentricity,
                'flagged': False
            }                
            measuredContours.append(measuredContour)

        print ("amount of contours: ", len(contours))

        def isTooFarFromMean(value, mean, deviation, numDeviations):
            return value > mean + numDeviations * deviation or value < mean - numDeviations * deviation

        dist = getattr(scipy.stats, 'norm')
        meanVar, deviationVar = dist.fit(areaVariations)
        print("variation mean: ", meanVar, ", and deviation: ", deviationVar)
        meanEcc, deviationEcc = dist.fit(eccentricities)
        print("eccentricity mean: ", meanEcc, ", and deviation: ", deviationEcc)
        measuredContours = list(
            filter(
                lambda x: not (isTooFarFromMean(x['areaVariation'], meanVar, deviationVar, 3) or 
                isTooFarFromMean(x['ellipseEccentricity'], meanEcc, deviationEcc, 3)), 
                measuredContours
                )
            )

        for measuredContour in measuredContours: 
            if isTooFarFromMean(measuredContour['areaVariation'], meanVar, deviationVar, 2):
                measuredContour['flagged'] = True
            if isTooFarFromMean(measuredContour['ellipseEccentricity'], meanEcc, deviationEcc, 2):
                measuredContour['flagged'] = True

        return measuredContours

    def showEdges(edge):
        global img
        vis = img.copy()
        vis = np.uint8(vis/2.)
        vis[edge != 0] = (0, 255, 0)
        #vis = cv.resize(vis, (0,0), fx=0.5, fy=0.5) 
        cv.imshow('edge', vis)

    def showContours(goodContours, flaggedContours, h, w):
        global img
        global levels
        #vis = np.zeros((h, w, 3), np.uint8)
        vis = img.copy()
        cv.drawContours( vis, goodContours, (-1, 2)[levels <= 0], (128,255,255), 3, cv.LINE_AA )
        cv.drawContours( vis, flaggedContours, (-1, 2)[levels <= 0], (0,0,255), 3, cv.LINE_AA )
        # vis = cv.resize(vis, (0,0), fx=0.5, fy=0.5) 
        cv.imshow('contours', vis)

    def update():
        global levels
        global thrs1
        global thrs2
        edge = cv.Canny(gray, thrs1, thrs2, apertureSize=5)
        h, w = edge.shape[:2]

        _, contours0, hierarchy = cv.findContours(edge, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        #contours = [cv.approxPolyDP(cnt, 3, True) for cnt in contours0]
        analyzedContours = analyzeContours(contours0)
        showEdges(edge)
        flaggedContours = []
        goodContours = []
        for analyzedContour in analyzedContours:
            if analyzedContour['flagged']:
                flaggedContours.append(analyzedContour['contour'])
            else:
                goodContours.append(analyzedContour['contour'])
        showContours(goodContours, flaggedContours, h, w)

    cv.imshow('image', img)
    cv.imshow('contours', img)
    cv.createTrackbar( "levels+3", "contours", 7, 7, updateLevels)
    cv.createTrackbar('thrs1', 'contours', 2000, 5000, updateThrs1)
    cv.createTrackbar('thrs2', 'contours', 4000, 5000, updateThrs2)

    update()
    cv.waitKey()
    cv.destroyAllWindows()