#!/usr/bin/env python
# encoding: utf-8


class Color(object):
    def __init__(self, r=0, g=0, b=0, time=0):
        self._col = (r, g, b)
        #self._col = tuple(map(lambda x: min(max(x, 0), 255), (r, g, b)))
        self._time = time

    ################
    #  Properties  #
    ################

    @property
    def red(self):
        return self._col[0]

    @property
    def green(self):
        return self._col[1]

    @property
    def blue(self):
        return self._col[2]

    def get_time(self):
        return self._time

    def set_time(self, time):
        self._time = time

    time = property(get_time, set_time)

    ###############
    #  Operators  #
    ###############

    def __eq__(self, rhs):
        return (self._col, self.time) == (rhs._col, rhs.time)

    def __iter__(self):
        return iter(self._col)

    def __repr__(self):
        return repr(self._col + tuple([self._time]))

    def __str__(self):
        return "{r} {g} {b}".format(r=self._col[0], g=self._col[1], b=self._col[2])

    def __add__(self, rhs):
        retv = Color(time=self.time)
        retv._col = tuple(map(lambda a, b: a + b, self._col, rhs._col))
        return retv

    def __sub__(self, rhs):
        return self + Color(r=-self.red, g=-self.green, b=-self.blue)
