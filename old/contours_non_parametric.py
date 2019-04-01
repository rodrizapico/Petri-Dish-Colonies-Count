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
import random
import itertools
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

import numpy as np
import cv2 as cv

import scipy
import scipy.stats

import sklearn.cluster
import sklearn.preprocessing

from sklearn import metrics

import matplotlib.pyplot as plt

if __name__ == '__main__':
    print(__doc__)

    default_file =  "./data/sample5.jpg" # sample#.jpg , smarties.png
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

    def showEdges(edge):
        global img
        vis = img.copy()
        vis = np.uint8(vis/2.)
        vis[edge != 0] = (0, 255, 0)
        vis = cv.resize(vis, (0,0), fx=0.3, fy=0.3) 
        cv.imshow('edge', vis)

    def showContours(analyzedContours, h, w):
        global img
        global levels
        # vis = np.zeros((h, w, 3), np.uint8)
        vis = img.copy()


        cluster_numbers = set(map(lambda x: x['cluster_number'], analyzedContours))

        clusters = {}
        for analyzedContour in analyzedContours:
            cluster_number = analyzedContour['cluster_number']
            if (not cluster_number in clusters.keys()):
                clusters[cluster_number] = []
            clusters[cluster_number].append(analyzedContour['contour'])

        for cluster_number in cluster_numbers:
            cluster = clusters[cluster_number]
            if cluster_number == -1:
                # Black used for noise.
                color = (255,255,255)
            else:
                color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
            cv.drawContours( vis, cluster, (-1, 2)[levels <= 0], color, 3, cv.LINE_AA )
            
        vis = cv.resize(vis, (0,0), fx=0.3, fy=0.3)
        cv.imshow('contours', vis)

    def analyzeContours(contours):

        measuredContours = []
        dbscanInput = []

        def contourFilterParams(contour):
            aspectRatio = 0
            MA = 0
            if len(contour) >= 5:
                (x, y), (ma, MA), angle = cv.fitEllipse(contour)
                aspectRatio = ma/MA

            # Color param
            mask = np.zeros(gray.shape,np.uint8)
            cv.drawContours(mask,[contour],0,255,-1)
            bc, gc, rc, _ = cv.mean(img, mask)
            color = bc + gc + rc

            return [MA, color]

        print("length before: ", len(contours))

        filterScanInput = list(map(lambda c: contourFilterParams(c), contours))

        filterScanInput = np.array(filterScanInput)
        filterScanInput = sklearn.preprocessing.RobustScaler().fit_transform(filterScanInput)

        # print ("filterScanInput normalized: ", filterScanInput)
        db = sklearn.cluster.DBSCAN(8.5, np.log(len(filterScanInput))).fit(filterScanInput)

        contours_mask = list(map(lambda x: x != -1, db.labels_))
        contours = list(itertools.compress(contours, contours_mask))

        print("length after: ", len(contours))

        for contour in contours:

            # Extent param
            cArea = cv.contourArea(contour)
            _, radius = cv.minEnclosingCircle(contour)
            circleArea = np.power(radius, 2) * np.pi
            extent = cArea / circleArea if circleArea > 0  else 0          

            # Eccentricity param
            eccentricity = 0
            if len(contour) >= 5:
                (x, y), (ma, MA), angle = cv.fitEllipse(contour)
                a = MA/2
                b = ma/2

                eccentricity = np.sqrt(1 - np.power(b,2)/np.power(a,2))
                eccentricity = np.round(eccentricity, 2)

            dbscanInput.append([extent, eccentricity])

            measuredContour = {
                'contour': contour,
                'areaVariation': extent,
                'ellipseEccentricity': eccentricity,
                'flagged_outlier': False,
                'flagged_not_core': False
            }
            measuredContours.append(measuredContour)

        print ("amount of contours: ", len(contours))

        X = np.array(dbscanInput)
        X = sklearn.preprocessing.MinMaxScaler().fit_transform(X)
        db = sklearn.cluster.DBSCAN(0.2, np.log(len(dbscanInput))).fit(X)

        core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True
        labels = db.labels_

        # Number of clusters in labels, ignoring noise if present.
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

        # print ("labels: ", labels)
        # print ("db.core_sample_indices_: ", db.core_sample_indices_)
        # print ("core_samples_mask: ", core_samples_mask)

        i = 0
        while i < len(measuredContours):
            measuredContours[i]['cluster_number'] = labels[i]
            measuredContours[i]['flagged_outlier'] = labels[i] == -1
            measuredContours[i]['flagged_not_core'] = not core_samples_mask[i]
            i += 1



        # Black removed and is used for noise instead.
        unique_labels = set(labels)
        colors = [plt.cm.Spectral(each)
                  for each in np.linspace(0, 1, len(unique_labels))]
        for k, col in zip(unique_labels, colors):
            if k == -1:
                # Black used for noise.
                col = [0, 0, 0, 1]

            class_member_mask = (labels == k)

            xy = X[class_member_mask & core_samples_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
                     markeredgecolor='k', markersize=14)

            xy = X[class_member_mask & ~core_samples_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
                     markeredgecolor='k', markersize=6)

        plt.title('Estimated number of clusters: %d' % n_clusters_)
        # plt.show()        







        return measuredContours

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
        showContours(analyzedContours, h, w)

    cv.imshow('image', img)
    cv.imshow('contours', img)
    cv.createTrackbar( "levels+3", "contours", 7, 7, updateLevels)
    cv.createTrackbar('thrs1', 'contours', 2000, 5000, updateThrs1)
    cv.createTrackbar('thrs2', 'contours', 4000, 5000, updateThrs2)

    update()
    cv.waitKey()
    cv.destroyAllWindows()