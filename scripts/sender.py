#!/usr/bin/env python
# encoding: utf-8

import multiprocessing
import subprocess
import time
import collections
import Queue

import color


TERMINAL_ITEM = None


class CatlightPipe(object):
    def __init__(self):
        self._pipe = subprocess.Popen(['/usr/bin/catlight', 'cat'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        print('** Created pipe to catlight (# {pid})'.format(pid=self._pipe.pid))

    def writeline(self, line='\n'):
        self._pipe.stdin.write(line.strip() + '\n')

    def terminate(self):
        self._pipe.communicate()
        print('** Catlight terminated (# {pid})'.format(pid=self._pipe.pid))


class SenderThread(multiprocessing.Process):
    def __init__(self):
        self._stack = []
        self._bklog = multiprocessing.Queue()
        self._queue = multiprocessing.Queue()
        self._pipe = CatlightPipe()
        multiprocessing.Process.__init__(self)

    def send(self, color_obj):
        'Send an iterable or a color to the catlight Queue.'
        if isinstance(color_obj, color.Color):
            self._stack.append(color_obj)
        elif isinstance(color_obj, collections.Iterable):
            for i in color_obj:
                self._stack.append(i)
        self._queue.put(color_obj)

    def list_queue(self):
        'List all jobs that are in the Queue. Returns a list of Colors.'
        try:
            while True:
                e = self._bklog.get_nowait()
                if not e:
                    break
                else:
                    self._stack.remove(e)
        except Queue.Empty:
            pass

        return self._stack

    def _execute_color_obj(self, color_obj):
        self._pipe.writeline(str(color_obj))
        if color_obj.time is not 0:
            time.sleep(color_obj.time / 1000.0)

        self._bklog.put(color_obj)

    def run(self):
        while True:
            e = self._queue.get()
            print('getting:', e)
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
    s = SenderThread()
    s.start()
    return s


if __name__ == '__main__':
    import color as c
    import effects as e

    '''
    l, r = [], []
    for v in range(256):
            l.append(c.Color(0, v, 0, 10))
            r.append(c.Color(0, 0, 255 - v, 10))

    sender = start_sender()
    #sender.send(l)
    #sender.send(c.Color(255, 0, 0, 1000))
    #sender.send(r)
    sender.send(e.SimpleFade(speed=100, color=c.Color(255, 0, 0)))

    #sender.send(c1)
    #sender.send(c1 + c2)
    #sender.send(c1 + c2 + c3)
    #sender.send(c.Color(0,0,0))

    sender.stop()
    '''

    print('...')
    sender = start_sender()
    print('...?')
    print(sender.list_queue())
    sender.send(c.Color(255, 0, 0, 1000))
    print(sender.list_queue())
    sender.send(c.Color(0, 0, 255, 5000))
    print(sender.list_queue())
    print(sender.send(e.SimpleFade()))
    time.sleep(1.2)
    print(sender.list_queue())
    sender.stop()

