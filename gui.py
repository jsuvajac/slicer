from __future__ import annotations

from wav import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk
)
from matplotlib.backend_bases import key_press_handler

import numpy as np

from tkinter import *
from tkinter import ttk

slice_dir = "slice"

class Window:
    def __init__(self, files):
        self.root = Tk()
        self.root.title("slicer")
        self.root.geometry('1080x750') 
        self.root.config(bg='lightgray')
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)

        # horizontal bars
        self.top_frame = Frame(self.root, width=1200, height=30, padx=5, pady=5, bg='orange')
        self.top_frame.pack(side=TOP, fill=X)
 
        self.middle_frame = Frame(self.root, width=1200, height=200, padx=5, pady=5, bg='darkorange')
        self.middle_frame.pack(side=TOP, fill=BOTH)

        self.bottom_frame = Frame(self.root, width=1200, height=100, padx=5, pady=5, bg='orange')
        self.bottom_frame.pack(side=TOP, fill=X)
 
        # bottom tray
        self.bottom_tray = Frame(self.root, width=1200, height=100, padx=5, pady=5, bg='orange')
        self.bottom_tray.pack(side=BOTTOM, fill=BOTH)
               
        # vertical bars in the middle
        self.file_frame = ttk.Frame(self.middle_frame, width=500, height=800)
        self.file_frame.pack(side=LEFT, fill=BOTH)

        self.plot_frame = ttk.Frame(self.middle_frame, width=500, height=400)
        self.plot_frame.pack(side=LEFT, fill=BOTH, expand=1)

        self.widget_frame = ttk.Frame(self.middle_frame, width=500, height=400)
        self.widget_frame.pack(side=LEFT, fill=BOTH)

        # quit btn
        button = ttk.Button(master=self.bottom_tray, text="Quit", command=self.root.quit)
        button.pack(side=LEFT, expand=1)

        self.fig = None
        self.canvas = None
        self.tree = None
        self.locators = []

        self.files = files
        self.slice_count = 0
        self.display_files(self.files)

        self.slice = Wav(files[0])

        self.gui_setup()


    def plot(self, display_spectral=False):
        if self.fig is not None:
            self.fig.clf()
        # wav

        if not display_spectral:
            self.fig = plt.figure(1)
            self.wav_plot = plt.subplot(111)
            self.wav_plot.plot(self.slice.slice_samples)
            #self.wav_plot.set_ylabel('amplitude')
            #self.wav_plot.axis('off')
            self.fig.set_facecolor('lightgray')
            self.setTitle("Select 2 cutting points")
        #spectrograph
        else:
            self.fig = plt.figure(1)
            self.wav_plot = plt.subplot(211)
            self.wav_plot.plot(self.slice.slice_samples)
            self.wav_plot.set_ylabel('amplitude')
            self.wav_plot.axis('off')
            self.fig.set_facecolor('lightgray')
            self.setTitle("Select 2 cutting points")
 
            self.spec_plot = plt.subplot(212)
            self.spec_plot.specgram(self.slice.slice_samples, Fs=self.slice.file.getframerate(), NFFT=1024)
            self.spec_plot.set_xlabel('time')
            self.spec_plot.set_ylabel('frequency')

        if self.canvas:
            self.canvas.draw()
        
   
    def gui_setup(self):
        self.plot()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('key_press_event', self.on_key)
        self.canvas.draw()
        #self.plot_toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame).pack(side=TOP, fill=X)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        #self.plot_toolbar.update()

        self.play_button = ttk.Button(master=self.widget_frame, text="Play", command=self.slice.play)
        self.play_button.pack(side=TOP)
        self.stop_button = ttk.Button(master=self.widget_frame, text="Stop", command=self.slice.stop)
        self.stop_button.pack(side=TOP)

        ttk.Label(self.widget_frame, text="-------------------------------------------").pack(side=TOP, expand=1)

        # speed
        self.speed_slider = IntVar()
        ttk.Label(self.widget_frame, text="speed up").pack(side=TOP)
        ttk.Label(self.widget_frame, textvariable=self.speed_slider).pack(side=TOP)
        ttk.Scale(self.widget_frame, from_=-10, to_=10, length=300, command=lambda s:self.speed_slider.set(int(float((s))))).pack(side=TOP)

        self.speed_button = ttk.Button(master=self.widget_frame, text="apply speed", command=self.on_speed_click)
        self.speed_button.pack(side=TOP)


        ttk.Label(self.widget_frame, text="-------------------------------------------").pack(side=TOP, expand=1)

        # slow
        self.slow_slider = IntVar()
        ttk.Label(self.widget_frame, text="slow down").pack(side=TOP)
        ttk.Label(self.widget_frame, textvariable=self.slow_slider).pack(side=TOP)
        ttk.Scale(self.widget_frame, from_=-10, to_=10, length=300, command=lambda s:self.slow_slider.set(int(float((s))))).pack(side=TOP)

        self.slow_button = ttk.Button(master=self.widget_frame, text="apply slow", command=self.on_slow_click)
        self.slow_button.pack(side=TOP)


        ttk.Label(self.widget_frame, text="-------------------------------------------").pack(side=TOP, expand=1)

        # repeats
        self.repeat_slider = IntVar()
        ttk.Label(self.widget_frame, text="repeats").pack(side=TOP)
        ttk.Label(self.widget_frame, textvariable=self.repeat_slider).pack(side=TOP)
        ttk.Scale(self.widget_frame, from_=-10, to_=10, length=300, command=lambda s:self.repeat_slider.set(int(float((s))))).pack(side=TOP)

        self.repeat_button = ttk.Button(master=self.widget_frame, text="apply repeats", command=self.on_repeat_click)
        self.repeat_button.pack(side=TOP)


        ttk.Label(self.widget_frame, text="-------------------------------------------").pack(side=TOP, expand=1)



        self.slice_button = ttk.Button(master=self.widget_frame, text="Slice", command=self.on_slice_click)
        self.slice_button.pack(side=TOP)

        ttk.Label(self.widget_frame, text="-------------------------------------------").pack(side=TOP, expand=1)

        self.write_button = ttk.Button(master=self.widget_frame, text="Write to file", command=self.on_write_slice_click)
        self.write_button.pack(side=TOP)



        ttk.Label(self.widget_frame, text="===========================================").pack(side=TOP, expand=1)


        self.reset_button = ttk.Button(master=self.widget_frame, text="Reset Sample", command=self.on_reset_click)
        self.reset_button.pack(side=TOP)

        ttk.Label(self.widget_frame, text="").pack(side=TOP, expand=1)


    def display_files(self,files):
        if not self.tree:
            self.tree = ttk.Treeview(self.file_frame)
            self.tree.bind("<Double-1>", self.on_file_select)
            self.tree.heading("#0",text="wav files",anchor=W)
            self.tree.pack(side=LEFT, fill=BOTH, expand=1)
        # clean
        for i in self.tree.get_children():
            self.tree.delete(i)
        # repopulate
        for f in files:
            self.tree.insert("", 0, text=f)

    def run(self):
        self.root.mainloop()

    def setTitle(self, s: str):
        self.wav_plot.set_title(s, fontsize=16)
        plt.suptitle(self.slice.path)
        plt.draw()


# EVENTS

    def on_file_select(self, event: Event):
        item = self.tree.selection()[0]
        file_path = self.tree.item(item,"text")
        print("you clicked on", file_path)
        self.slice = Wav(file_path)
        self.plot()
        self.canvas.draw()
        self.play_button['command'] = self.slice.play
        self.stop_button['command'] = self.slice.stop

    def on_key(self, event: Event):
        key_press_handler(event, self.canvas)
        print('you pressed', event.key, event.xdata, event.ydata)
        if event.key == "escape":
            self.root.quit()

    def on_click(self, event: Event):
        # left
        if event.button == 1 and type(event.xdata) is np.float64:
            self.locators.append(int(event.xdata))
            if len(self.locators) > 2:
                self.locators.pop(0)
                self.fig.clf()
                self.plot()
            print(self.locators)
            for x in self.locators:
                self.wav_plot.axvline(x=x, color = 'r')
        # right
        elif type(event.xdata) is np.float64:
            self.locators.append(int(event.xdata))
            self.reset_plot()

        self.canvas.draw()

    def reset_plot(self):
        self.locators = []
        self.fig.clf()
        self.plot()

    def on_slice_click(self):
        print(self.locators)
        self.locators = np.sort(self.locators)
        if len(self.locators) == 2:
            if self.locators[0] < 0:
                self.locators[0] = 0
            self.slice.apply_slice(self.locators[0], self.locators[1])
        self.reset_plot()


    def on_speed_click(self):
        self.slice.apply_speed_change(self.speed_slider.get())
        self.reset_plot()

    def on_slow_click(self):
        factor = self.slow_slider.get()
        print(factor)
        self.slice.apply_speed_change(1/factor)
        self.reset_plot()


    def on_repeat_click(self):
        self.slice.apply_repeat(self.repeat_slider.get())
        self.reset_plot()

    
    def on_write_slice_click(self):
        print('writing slice')
        path = slice_dir+"/"+"slice"

        self.files.append(path)
        self.slice.write_slice(path)

        self.display_files(self.files)

    def on_reset_click(self):
        self.slice.reset_buffer()
        self.reset_plot()