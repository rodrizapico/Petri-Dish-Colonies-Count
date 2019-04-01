#!/usr/bin/env python

from tkinter import *

import contour_analyzer as ctan
import tkinter_helper as tkhelp
import webcolors

class MainWindow:
    def __init__(self):
        self.analyzer = ctan.ContourAnalyzer()

        self.window = Tk()
        self.window.title("Sample")

        # add the panel that will show our original image
        self.original_panel = tkhelp.ImagePanel.buildDefault(self.window, self.analyzer.original)
        self.analyzer.addObserver(self.original_panel)

        # add the panel that will show the detected contours
        self.analyzed_panel = tkhelp.ImagePanel.buildDefault(self.window, self.analyzer.analyzed)
        self.analyzer.addObserver(self.analyzed_panel)

        # add the panel that will show extra information
        self.info_panel = tkhelp.TextPanel.buildDefault(self.window, self.getClustersText)
        self.analyzer.addObserver(self.info_panel)

        # add a file selector
        self.selector = tkhelp.FileSelectorButton.buildDefault(self.window, self.analyzer.path)

        # add config options
        self.brightness_slider = tkhelp.BoundSlider.buildDefault(self.window, 
            self.analyzer.brightness,
            label = "Brightness")
        self.analyzer.addObserver(self.brightness_slider)

        self.contrast_slider = tkhelp.BoundSlider.buildDefault(self.window, 
            self.analyzer.contrast,
            label = "Contrast")
        self.analyzer.addObserver(self.contrast_slider)

        self.sharpness_slider = tkhelp.BoundSlider.buildDefault(self.window, 
            self.analyzer.sharpness,
            label = "Sharpness",
            to = 4)
        self.analyzer.addObserver(self.sharpness_slider)        

        self.pre_eps_slider = tkhelp.BoundSlider.buildDefault(self.window, 
            self.analyzer.pre_eps,
            label = "Preliminary DBScan Epsilon",
            to = 10)
        self.analyzer.addObserver(self.pre_eps_slider)

        self.eps_slider = tkhelp.BoundSlider.buildDefault(self.window, 
            self.analyzer.eps,
            label = "DBScan Epsilon",
            to = 1)
        self.analyzer.addObserver(self.eps_slider)

        self.ths1_slider = tkhelp.BoundSlider.buildDefault(self.window, 
            self.analyzer.ths1,
            label = "Canny Threshold 1",
            to = 10000)
        self.analyzer.addObserver(self.ths1_slider)

        self.ths2_slider = tkhelp.BoundSlider.buildDefault(self.window, 
            self.analyzer.ths2,
            label = "Canny Threshold 2",
            to = 10000)
        self.analyzer.addObserver(self.ths2_slider)

        # add reset button
        self.reset_button = Button(self.window, text = "Reset", command = self.analyzer.reset)
        self.reset_button.pack(padx = 10, pady = 10)

    def getClustersText(self):

        def get_colour_name(rgb_triplet):
            min_colours = {}
            for key, name in webcolors.css21_hex_to_names.items():
                r_c, g_c, b_c = webcolors.hex_to_rgb(key)
                rd = (r_c - rgb_triplet[2]) ** 2
                gd = (g_c - rgb_triplet[1]) ** 2
                bd = (b_c - rgb_triplet[0]) ** 2
                min_colours[(rd + gd + bd)] = name
            return min_colours[min(min_colours.keys())]

        if not self.analyzer.clusters():
            return "Please select a file to analyze"
        text = "Found " + str(len(self.analyzer.clusters())) + " clusters \n"
        for cluster in self.analyzer.clusters():
            color = cluster.getColor()
            text += "        Size of cluster: " + str(len(cluster.contours)) + "\n"
            text += "                color: (" + str(int(color[2]))
            text += ", " + str(int(color[1]))
            text += ", " + str(int(color[0])) + ")\n"
            text += "                your cluster is " + str(get_colour_name(color)) + "\n"
        return text

    def run(self):
        self.window.mainloop()

if __name__ == '__main__':
    main_window = MainWindow()
    main_window.run()