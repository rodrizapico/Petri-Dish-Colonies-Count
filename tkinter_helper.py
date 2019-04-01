from tkinter import *
from tkinter import filedialog

import image_processing as imgpr

class BoundCheckbutton(Checkbutton):

    def __init__(self, master, binding, **kw):
        self.binding = binding
        self.value = BooleanVar()
        kw["variable"] = self.value
        kw["command"] = self.toggleBinding
        super().__init__(master, kw)

    def toggleBinding(self):
        self.binding(self.value.get())

class BoundSlider(Scale):

    @staticmethod
    def buildDefault(master, binding, **kw):
        defaults = {
            'orient': HORIZONTAL, 
            'label': 'label', 
            'from_': 0, 
            'to': 2, 
            'resolution': 0.01
        }
        kw = {**defaults , **kw}

        slider = BoundSlider(master, binding, **kw)
        slider.pack(padx = 10, pady = 10)
        return slider

    def __init__(self, master, binding, **kw):
        self.binding = binding
        super().__init__(master, kw)
        self.bind("<ButtonRelease-1>", self.setValue)
        self.set(self.binding())

    def setValue(self, e):
        self.binding(self.get())

    def notify(self):
        self.set(self.binding())

class FileSelectorButton(Button):

    @staticmethod
    def buildDefault(master, binding):
        selector = FileSelectorButton(master, binding, text = "Select an image")
        selector.pack(padx = 10, pady = 10)
        return selector

    def __init__(self, master, binding, **kw):
        self.binding = binding
        kw["command"] = self.selectImage
        super().__init__(master, kw)

    def selectImage(self):
        path = filedialog.askopenfilename()
        if len(path) > 0:
            self.binding(path)

class ImagePanel(Label):

    @staticmethod
    def buildDefault(master, binding):
        panel = ImagePanel(master, binding, width = 640, height= 640)
        panel.pack(side = LEFT, padx = 10, pady = 10)
        return panel

    def __init__(self, master, binding, default_path = "./data/blank.jpg", **kw):
        self.binding = binding

        thumb_width = kw['width'] if 'width' in kw else 300
        thumb_height = kw['height'] if 'height' in kw else 300
        self.thumb_size = (thumb_width, thumb_height)

        self.image = imgpr.ImageWrapper.fromPath(default_path).toViewFormat(self.thumb_size)
        kw['image'] = self.image

        super().__init__(master, kw)

    def notify(self):
        self.image = self.binding().toViewFormat(self.thumb_size)
        self.configure(image = self.image)

class TextPanel(Label):

    @staticmethod
    def buildDefault(master, binding):
        panel = TextPanel(master, binding)
        panel.pack(padx = 10, pady = 10)
        return panel

    def __init__(self, master, binding, **kw):
        self.binding = binding
        self.text = binding()
        kw['text'] = self.text
        super().__init__(master, kw)

    def notify(self):
        self.text = self.binding()
        self.configure(text = self.text)
        