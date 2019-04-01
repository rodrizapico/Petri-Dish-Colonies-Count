import contours as cts
import image_processing as imgpr




import cv2 as cv




class ContourAnalyzer:

    def __init__(self):

        # Inputs
        self.path = self.buildBindableAttribute('__path', initial_value = None)
        self.brightness = self.buildBindableAttribute('__brightness', initial_value = 1)
        self.contrast = self.buildBindableAttribute('__contrast', initial_value = 1)
        self.sharpness = self.buildBindableAttribute('__sharpness', initial_value = 1)
        self.pre_eps = self.buildBindableAttribute('__pre_eps', initial_value = 0.5)
        self.eps = self.buildBindableAttribute('__eps', initial_value = 0.2)
        self.ths1 = self.buildBindableAttribute('__ths1', initial_value = 0)
        self.ths2 = self.buildBindableAttribute('__ths2', initial_value = 3000)

        # Outputs
        self.original = self.buildBindableAttribute('__original', input = False)
        self.analyzed = self.buildBindableAttribute('__analyzed', input = False)
        self.clusters = self.buildBindableAttribute('__clusters', input = False)

        #Config
        contour_detector = cts.CannyContourDetector(self.ths1(), self.ths2())
        self.contour_factory = cts.ContourFactory(contour_detector)
        #self.contour_scanner = cts.ContourSingleClusterScanner() 
        self.contour_scanner = cts.ContourDBScanner(self.pre_eps(), self.eps())
        self.__observers = []

    def addObserver(self, obs):
        self.__observers.append(obs)

    def removeObserver(self, obs):
        self.__observers.remove(obs)

    def notifyObservers(self):
        for obs in self.__observers:
            obs.notify()

    def reset(self):
        # Inputs
        self.brightness(1)
        self.contrast(1)
        self.sharpness(1)
        self.pre_eps(0.5)
        self.eps(0.2)
        self.ths1(2000)
        self.ths2(4000)
        self.notifyObservers()

    def buildBindableAttribute(self, attr_name, input = True, initial_value = None):
        setattr(self, attr_name, initial_value)
        def bindableAttr(value = None):
            if not value:
                return getattr(self, attr_name)
            setattr(self, attr_name, value)
            if input:
                self.update()
        return bindableAttr

    def updateContourScanner(self):
        contour_detector = cts.CannyContourDetector(self.ths1(), self.ths2())
        self.contour_factory = cts.ContourFactory(contour_detector)

        if isinstance(self.contour_scanner, cts.ContourDBScanner):
            self.contour_scanner.pre_eps = self.pre_eps()
            self.contour_scanner.eps = self.eps()

    def update(self):
        if not self.path():
            return
        self.updateContourScanner()
        self.preprocessImg()
        self.analyzeImg()
        self.notifyObservers()

    def preprocessImg(self):
        img = imgpr.ImageWrapper.fromPath(self.path())
        img.resize((1000, 1000))
        img.brightness(self.brightness())
        img.contrast(self.contrast())
        img.sharpness(self.sharpness())
        
        # img.autocontrast()
        # img.invert()

        self.original(img)

    def analyzeImg(self):
        img = self.original().copy()





        # Testing shit out
        # src_gray = cv.cvtColor(img.toModelFormat(), cv.COLOR_BGR2GRAY)
        # circles = cv.HoughCircles(src_gray, cv.HOUGH_GRADIENT, 1, 90, param1=100, param2=15, minRadius=0, maxRadius=70)

        # vis = self.original().copy().reset().color(0).toModelFormat()

        # for i in circles[0,:]:
        #     # draw the outer circle
        #     cv.circle(vis,(i[0],i[1]),i[2],(0,255,0),2)
        #     # draw the center of the circle
        #     cv.circle(vis,(i[0],i[1]),2,(0,0,255),3)            
        # self.analyzed(imgpr.ImageWrapper.fromModel(vis))






        contours = self.contour_factory.build(img.toModelFormat())
        clusters = self.contour_scanner.scan(contours)
        self.clusters(clusters)

        self.drawResults()

    def drawResults(self):
        vis = self.original().copy().reset().resize((1000, 1000)).color(0).toModelFormat()
        
        if self.clusters():
            for cluster in self.clusters():
                vis = cluster.drawOnImage(vis)
        self.analyzed(imgpr.ImageWrapper.fromModel(vis))