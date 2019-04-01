import cv2 as cv
import numpy as np
from PIL import Image
from PIL import ImageTk
from PIL import ImageEnhance
from PIL import ImageOps 

class ImageWrapper:

    @staticmethod
    def fromPath(path):
        image = Image.open(path).convert('RGB')
        return ImageWrapper(image)

    @staticmethod
    def fromImage(image):
        return ImageWrapper(image)

    @staticmethod
    def fromModel(model_image):
        image = cv.cvtColor(model_image, cv.COLOR_BGR2RGB)
        image = Image.fromarray(image)        
        return ImageWrapper(image)

    def __init__(self, image):
        self.image = image.copy()
        self.original = self.image.copy()

    def copy(self):
        copy = ImageWrapper.fromImage(self.image)
        copy.original = self.original
        return  copy

    def reset(self):
        self.image = self.original.copy()
        return self

    def brightness(self, factor):
        self.image = ImageEnhance.Brightness(self.image).enhance(factor)
        return self

    def color(self, factor):
        self.image = ImageEnhance.Color(self.image).enhance(factor)
        return self

    def contrast(self, factor):
        self.image = ImageEnhance.Contrast(self.image).enhance(factor)
        return self

    def sharpness(self, factor):
        self.image = ImageEnhance.Sharpness(self.image).enhance(factor)
        return self

    def autocontrast(self):
        self.image = ImageOps.autocontrast(self.image)
        return self

    def invert(self):
        self.image = ImageOps.invert(self.image)
        return self

    def equalize(self):
        self.image = ImageOps.equalize(self.image)
        return self

    def resize(self, new_size):
        self.image.thumbnail(new_size)
        return self

    def toModelFormat(self):
        open_cv_image = np.array(self.image) 
        return cv.cvtColor(open_cv_image, cv.COLOR_RGB2BGR)

    def toViewFormat(self, thumb_size = (300, 300)):
        self.image.thumbnail(thumb_size)
        return ImageTk.PhotoImage(self.image)
