#!/usr/bin/env python
# encoding: utf-8

import multiprocessing
import subprocess
import time
import logging
import collections


import color


TERMINAL_ITEM = None


class CatlightPipe(object):
    def __init__(self):
        self._pipe = subprocess.Popen(['/usr/bin/catlight', 'cat'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        logging.warn('** Created pipe to catlight (# {pid})'.format(
            pid=self._pipe.pid))

    def writeline(self, line='\n'):
        self._pipe.stdin.write(line.strip() + '\n')

    def terminate(self):
        self._pipe.communicate()
        logging.warn('** Catlight terminated (# {pid})'.format(
            pid=self._pipe.pid))


class SenderThread(multiprocessing.Process):
    def __init__(self):
        self._queue = multiprocessing.Queue()
        self._pipe = CatlightPipe()
        multiprocessing.Process.__init__(self)

    def send(self, color_obj):
        self._queue.put(color_obj)

    def _execute_color_obj(self, color_obj):
        self._pipe.writeline(str(color_obj))
        if color_obj.time is not 0:
            time.sleep(color_obj.time / 1000.0)

    def run(self):
        while True:
            e = self._queue.get()
            if e is TERMINAL_ITEM:
                break
            elif isinstance(e, color.Color):
                self._execute_color_obj(e)
            elif isinstance(e, collections.Iterable):
                for i in e:
                    self._execute_color_obj(i)
            else:
                raise ValueError('Iterable or color.Color() needed')

    def stop(self):
        self._queue.put(TERMINAL_ITEM)
        self.join()
        self._pipe.terminate()


def start_sender():
    sender = SenderThread()
    sender.start()
    return sender


if __name__ == '__main__':
    sender = start_sender()
    import color as c
    import effects as e

    l, r = [], []
    for v in range(256):
            l.append(c.Color(0, v, 0, 10))
            r.append(c.Color(0, 0, 255 - v, 10))

    #sender.send(l)
    #sender.send(c.Color(255, 0, 0, 1000))
    #sender.send(r)
    sender.send(e.SimpleFade(color=c.Color(255, 0, 0)))

    logging.warn('** Waiting to finish.')
    sender.stop()
