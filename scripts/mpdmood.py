#!/usr/bin/env python2
# encoding: utf-8


from itertools import izip_longest


def grouper(iterable, n, fillvalue=None):
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(*args, fillvalue=fillvalue)


def read_moodbar(path):
    rgbs = []
    with open(path, 'rb') as f:
        for r, g, b in grouper(f.read(), n=3):
            rgbs.append((ord(r), ord(g), ord(b)))
    return rgbs


def convert_to_dict(dump):
    d = {}
    for line in dump.splitlines():
        try:
            key, value = line.strip().split(':', 1)
            d[key] = value
        except ValueError:
            pass
    return d


def read_current_song():
    import telnetlib
    client = telnetlib.Telnet(host='localhost', port=6600)
    client.read_until(b'OK')
    client.write(b'currentsong\n')
    current_song = convert_to_dict(client.read_until('OK\n'))
    client.write(b'status\n')
    status = convert_to_dict(client.read_until('OK\n'))
    client.close()
    return current_song['file'].strip(), int(current_song['Time']), float(status['elapsed'])


if __name__ == '__main__':
    import sender
    import sys
    import os
    from color import Color
    import subprocess
    # from effects import SimpleFade, KaminFeuerDerLust

    uri, time, elapsed = read_current_song()
    # sys.exit(0)
    percent = int((elapsed / time) * 1000)

    # Sender Queue
    SENDER = sender.start_sender()

    try:
        os.remove('/tmp/mood.file')
    except OSError:
        pass

    print('Time', uri, time, elapsed, percent, '/home/sahib/hd/music/clean/' + uri)
    subprocess.call([
        '/usr/bin/moodbar',
        '/home/sahib/hd/music/clean/' + uri,
        '-o', '/tmp/mood.file'
    ])


    moodbar = read_moodbar('/tmp/mood.file')
    moodbar = moodbar[percent:]

    for r, g, b in moodbar:
        # print(r, g, b)
        SENDER.send(Color(r, g, b, time))

    SENDER.send(Color(0, 0, 0, 1))
