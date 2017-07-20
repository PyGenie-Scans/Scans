#!/usr/bin/python2
"""A demo of proper multiprocessing matplotlib"""
from __future__ import print_function
from multiprocessing import Process, Pipe
import threading
import numpy as np

import matplotlib.pyplot as plt


class ProcessPlotter(object):
    """
    This object maintains a separate a separate process at the OS level
    which manages a matplotlib plot. This is an incredibly stupid way
    to get around the threading limitations of matplotlib, but it's
    also the best that we've found.

    Parameters
    ----------

    rehome : bool
      If true, the graph will recenter itself every time a new point
      is added.  Otherwise, the plot will remain where the user left
      it, but the home functionality will not be updated after the user
      moves the graph.
    """
    def __init__(self, rehome=False):
        self.x = []
        self.y = []

        self.pipe = None
        self.fig = None
        self.axis = None
        self.rehome = rehome

    def poll_draw(self):
        """
        Update the graph with the latest commands
        off the process channel
        """

        while True:
            if not (self.pipe and self.pipe.poll()):
                break

            command = self.pipe.recv()

            if command is None:
                self.pipe.send((self.x, self.y, self.fig))
                return False

            else:
                self.x.append(command[0])
                self.y.append(command[1])
                self.axis.plot(self.x, self.y, 'ro')
                if self.rehome:
                    self.axis.set_xlim(min(self.x), max(self.x))
                    self.axis.set_ylim(min(self.y), max(self.y))

        self.fig.canvas.draw()
        self.fig.canvas.show()
        threading.Timer(0.5, self.poll_draw).start()

    def __call__(self, pipe):

        self.pipe = pipe

        threading.Timer(0.5, self.poll_draw).start()
        self.fig, self.axis = plt.subplots()
        plt.show()


class NBPlot(object):
    """
    A non-blocking plot to get around the threading limitations of
    matplotlib.
    """
    def __init__(self, **kwargs):
        self.plot_pipe, plotter_pipe = Pipe()
        self.plotter = ProcessPlotter(**kwargs)
        self.plot_process = Process(target=self.plotter,
                                    args=(plotter_pipe,))
        # self.plot_process.daemon = True
        self.plot_process.start()

    def __call__(self, data):
        self.plot_pipe.send(data)

    def join(self):
        """Close the plot and get the results from it"""
        if not self.plot_process.daemon:
            return

        self.plot_pipe.send(None)
        result = self.plot_pipe.recv()
        self.plot_process.join()
        return result


def main():
    """A simple test function of NBPlot"""
    plot = NBPlot(rehome=False)
    boondoggle = np.arange(0, 2e6, dtype=np.int64)
    for i in range(10):
        plot([i, i**2])
        for _ in range(30):
            boondoggle = np.sin(boondoggle**2)
    return plot.join()


if __name__ == '__main__':
    main()
