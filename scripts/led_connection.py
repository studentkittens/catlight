import subprocess
import threading


led = subprocess.Popen("sudo /usr/bin/catlight cat", stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
sendLock = threading.Lock()


def __clamp(value):
    return max(0, min(abs(value), 255))


def send(r, g, b):
    sendLock.acquire()
    led.stdin.write('{0} {1} {2}\n'.format(
        __clamp(r),
        __clamp(g),
        __clamp(b)))
    sendLock.release()


def on():
    send(255, 255, 255)


def off():
    send(0, 0, 0)


def close():
    led.close()
