#!/usr/bin/env python
# encoding: utf-8

import color
import random


class SimpleFade(object):
    '''
    A simple Fade effect. Goes from 0 to 255 and back.
    It is configurable via a speed factor and a colormask.
    '''
    def __init__(self, speed=1.0, color=color.Color(255, 255, 255)):
        '''
        :speed: A speed factor, per default is 1.0, lower means slower.
        :color: A color mask. Default is white.
        '''
        self._speed = speed
        self._col = tuple(map(lambda v: v / 255.0, color))

    def __iter__(self):
        'Implementation. Just throw this into the Queue.'
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


class KaminFeuerDerLust(object):
    def __iter__(self):
        def calc_color(t, num=1024, fac=1.0, jitter=20):
            jitter_fac = random.randrange(-jitter, jitter)
            kamin_func = lambda x: -255./262144 * ((x - num/2) ** 2) + 255
            return fac * (kamin_func(t) + jitter_fac)

        NUM = 1024
        for t in range(NUM):
            r = calc_color(t, num=NUM, fac=1.0, jitter=50)
            g = calc_color(t, num=NUM, fac=0.15, jitter=100)
            b = calc_color(t, num=NUM, fac=0.01, jitter=10)

            yield color.Color(r, g, b, time=15)

        # Off:
        yield color.Color(0, 0, 0, time=20)


class Repeater(object):
    def __init__(self, effect, count=10):
        self._effect = effect
        self._count = count

    def __iter__(self):
        for i in range(self._count):
            for col in self._effect:
                yield col
