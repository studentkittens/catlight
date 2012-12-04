#!/usr/bin/env python
# encoding: utf-8

import color


class SimpleFade(object):
    def __init__(self, color=color.Color(255, 255, 255)):
        self._col = tuple(map(lambda v: v / 255.0, color))

    def __iter__(self):
        for i in range(256):
            r = self._col[0] * i
            g = self._col[1] * i
            b = self._col[2] * i
            yield color.Color(r, g, b)

        for i in range(255, -1, -1):
            r = self._col[0] * i
            g = self._col[1] * i
            b = self._col[2] * i
            yield color.Color(r, g, b)
