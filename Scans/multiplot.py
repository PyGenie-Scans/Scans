#!/usr/bin/python2
"""A demo of proper multiprocessing matplotlib"""
from __future__ import print_function
import time
from multiprocessing import Process, Pipe
import numpy as np

import matplotlib
matplotlib.use('GtkAgg')
import matplotlib.pyplot as plt
import gobject


class ProcessPlotter(object):
    def __init__(self, rehome=False):
        self.x = []
        self.y = []

        self.pipe = None
        self.fig, self.ax = plt.subplots()
        self.gid = gobject.timeout_add(1000, self.poll_draw())
        self.rehome = rehome

    def terminate(self):
        plt.close('all')

    def poll_draw(self):

        def call_back():
            while 1:
                if not self.pipe.poll():
                    break

                command = self.pipe.recv()
                print(command)

                if command is None:
                    self.terminate()
                    print("Terminated")
                    self.pipe.send((self.x, self.y))
                    return False

                else:
                    self.x.append(command[0])
                    self.y.append(command[1])
                    self.ax.plot(self.x, self.y, 'ro')
                    if self.rehome:
                        self.ax.set_xlim(min(self.x), max(self.x))
                        self.ax.set_ylim(min(self.y), max(self.y))


            self.fig.canvas.draw()
            return True

        return call_back

    def __call__(self, pipe):
        print('starting plotter...')

        self.pipe = pipe

        print('...done')
        plt.show()


class NBPlot(object):
    def __init__(self, **kwargs):
        self.plot_pipe, plotter_pipe = Pipe()
        self.plotter = ProcessPlotter(**kwargs)
        self.plot_process = Process(target=self.plotter,
                                    args=(plotter_pipe,))
        self.plot_process.daemon = True
        self.plot_process.start()

    def __call__(self, data):
        self.plot_pipe.send(data)

    def __del__(self):
        print("Deleting")
        self.plot_pipe.send(None)
        x, y = self.plot_pipe.recv()
        print(x, y)
        self.plot_process.join()
        # plt.plot(x, y)
        # plt.show()


def main():
    pl = NBPlot(rehome=False)
    boondoggle = np.arange(0, 1e7, dtype=np.uint64)
    for ii in range(10):
        pl([ii, ii**2])
        for _ in range(30):
            boondoggle = np.sin(boondoggle**2)

if __name__ == '__main__':
    main()
