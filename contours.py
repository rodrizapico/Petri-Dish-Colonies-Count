import cv2 as cv
import numpy as np
import sklearn.preprocessing
import sklearn.cluster
import itertools

class CannyContourDetector:

    def __init__(self, threshold1, threshold2):
        self.threshold1 = threshold1
        self.threshold2 = threshold2

    def  process(self, img):
        grayscale_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        grayscale_img = cv.bilateralFilter(grayscale_img, 25, 20, 20)
        edges = cv.Canny(grayscale_img, self.threshold1, self.threshold2, apertureSize=7, L2gradient=True)
        _, contours, hierarchy = cv.findContours(edges, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
        contours = [ c for idx, c in enumerate(contours) if hierarchy[0][idx][2] >= 0]
        
        return contours

class ContourFactory:

    def __init__(self, contour_detector):
        self.contour_detector = contour_detector
    

    def build(self, img):
        raw_contours = self.contour_detector.process(img)
        contours = [ Contour(rc, img) for rc in raw_contours ]
        return contours

class Contour:

    def __init__(self, contour_points, img):
        self.points = contour_points
        self.img = img

        # Mayor axis, excentricity params
        self.eccentricity = 0
        self.mayor_axis = 0
        if len(self.points) >= 5:
            (x, y), (ma, MA), angle = cv.fitEllipse(self.points)
            self.mayor_axis = MA / 2
            self.minor_axis = ma / 2
            self.eccentricity = np.sqrt(1 - np.power(self.minor_axis, 2) / np.power(self.mayor_axis, 2))


        # Color params
        grayscale_img = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        mask = np.zeros(grayscale_img.shape, np.uint8)
        cv.drawContours(mask,[self.points],0,255,-1)
        self.blue_color, self.green_color, self.red_color, _ = cv.mean(self.img, mask)
        self.mean_color = self.blue_color + self.green_color + self.red_color

        # Extent param
        self.area = cv.contourArea(self.points)
        _, radius = cv.minEnclosingCircle(self.points)
        circleArea = np.power(radius, 2) * np.pi
        self.extent = self.area / circleArea if circleArea > 0  else 0

class Cluster:

    def __init__(self, contours):
        self.contours = contours

    def getRaw(self):
        return [ c.points for c in self.contours ]

    def getColor(self):
        # return (0, 0, 255)
        return (self.contours[0].blue_color, self.contours[0].green_color, self.contours[0].red_color)

    def drawOnImage(self, image):
        raw_cluster = self.getRaw()
        color = self.getColor()
        # color = (0, 0, 255)
        cv.drawContours(image, raw_cluster, -1, color, 2, cv.LINE_AA)
        return image

class ContourDBScanner:

    def __init__(self, pre_eps, eps):
        self.pre_eps = pre_eps
        self.eps = eps

    def scan(self, contours):

        if len(contours) == 0:
            print('no contours')
            return []

        # Initial filter to weed out mayor outliers
        pre_scan_input = [ [c.mayor_axis, c.mean_color] for c in contours ]
        pre_scan_input = sklearn.preprocessing.RobustScaler().fit_transform(pre_scan_input)
        db = sklearn.cluster.DBSCAN(self.pre_eps, np.log(len(pre_scan_input))).fit(pre_scan_input)
        contours = list(itertools.compress(contours, [ x != -1 for x in db.labels_ ]))

        # Actual dbscan to get our clusters
        db_scan_input = [ [c.red_color, c.green_color, c.blue_color] for c in contours ]
        db_scan_input = sklearn.preprocessing.MinMaxScaler().fit_transform(db_scan_input)
        db = sklearn.cluster.DBSCAN(self.eps, np.log(len(db_scan_input))).fit(db_scan_input)
        clusters = { cluster_number:[] for cluster_number in np.unique(db.labels_) }
        for idx, contour in enumerate(contours):
            contour.cluster = db.labels_[idx]
            clusters[contour.cluster].append(contour)

        clusters = [ Cluster(cluster_contours) for cluster_contours in clusters.values()]
        return clusters

class ContourSingleClusterScanner:

    def scan (self, contours):
        return [ Cluster(contours) ]
 