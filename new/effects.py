#!/usr/bin/env python
# encoding: utf-8

import color

class SimpleFade(object):
    def __init__(self, speed=1.0, color=color.Color(255, 255, 255)):
        self._speed = speed
        self._col = tuple(map(lambda v: v / 255.0, color))

    def __iter__(self):
        for i in range(int(256 / self._speed)):
            r = self._col[0] * i * self._speed
            g = self._col[1] * i * self._speed
            b = self._col[2] * i * self._speed
            yield color.Color(r, g, b)

        for i in range(int(255 / self._speed), -1, -1):
            r = self._col[0] * i * self._speed
            g = self._col[1] * i * self._speed
            b = self._col[2] * i * self._speed
            yield color.Color(r, g, b)
