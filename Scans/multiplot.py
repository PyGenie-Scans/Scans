#!/usr/bin/python2
"""A demo of proper multiprocessing matplotlib"""
from __future__ import print_function
from multiprocessing import Process, Pipe
from logging import warning
import sys
import threading
import numpy as np

import matplotlib.pyplot as plt

# IBEX doesn't report a proper path for sys.executable
# This breaks multiprocessing, since it doesn't know
# where to find python to spawn a copy
if sys.executable == '':
    sys.executable = "C:/Instrument/Apps/Python/python.exe"


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
                del self.fig
                self.pipe.send((self.x, self.y))
                return None
            elif isinstance(command, tuple):
                if command[0] == "clf":
                    self.axis.cla()
                    continue
                if hasattr(self.axis, command[0]):
                    getattr(self.axis, command[0])(*command[1], **command[2])
                elif hasattr(self.fig, command[0]):
                    getattr(self.fig, command[0])(*command[1], **command[2])

        self.fig.canvas.draw()
        self.fig.canvas.show()
        threading.Timer(0.5, self.poll_draw).start()
        return None

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
        warning("Python will soon give an Error message about get_block_names."
                " Please ignore that error message.  Everything is working as"
                " expected.")
        self.plotter = ProcessPlotter(**kwargs)
        self.plot_process = Process(target=self.plotter,
                                    args=(plotter_pipe,))
        self.plot_process.daemon = True
        self.plot_process.start()

    def __call__(self, data):
        self.plot_pipe.send(data)

    def join(self):
        """Close the plot and get the results from it"""

        self.plot_pipe.send(None)
        result = self.plot_pipe.recv()
        self.plot_pipe.close()
        return result

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            """
            Send the appropriate command to the separate matplotlib process
            """
            self.plot_pipe.send((name, args, kwargs))
        return wrapper

    def __del__(self):
        self.join()


def main():
    """A simple test function of NBPlot"""
    plot = NBPlot(rehome=False)
    boondoggle = np.arange(0, 5e6, dtype=np.int64)
    xs = []
    ys = []
    for i in range(10):
        xs.append(i)
        ys.append(i**2)
        plot.clear()
        plot.set_xlim(0, 10)
        plot.plot(xs, ys)
        plot.errorbar(xs, [y + 3 for y in ys],
                      [4 for y in ys], fmt="rd")
        print(i)
        for _ in range(30):
            boondoggle = np.sin(boondoggle**2)
    plot.savefig("meta_test.png")
    return plot.join()


if __name__ == '__main__':
    main()
