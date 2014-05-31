#!/usr/bin/env python

# gobject
import dbus
import gobject
import dbus.mainloop.glib

# stdlib
import re
import time

# own
import sender
from color import Color
from effects import SimpleFade, KaminFeuerDerLust


# Sender Queue
SENDER = sender.start_sender()


# Actual uIDs are used, not aliases
buddy_reactions = {
    r'christoph.*\.nullcat\.de.*': KaminFeuerDerLust(),
    r'digitalkraut.*': SimpleFade(color=Color(255, 0, 255)),
    r'serztle.*': SimpleFade(color=Color(171, 243, 15)),
    r'mausmaki.*': SimpleFade(color=Color(255, 0, 0)),
    r'bubblebee.*': SimpleFade(color=Color(255, 127, 0))
}


class Listener:
    def __init__(self):
        self.__bus = dbus.SessionBus()
        self.__bus.add_signal_receiver(self.received_msg,
            dbus_interface="im.pidgin.purple.PurpleInterface",
            signal_name="ReceivedImMsg"
        )

    def received_msg(self, account, sender, message, conversation, flags):
        print(account, sender)
        for regex, effect in buddy_reactions.items():
            if re.search(regex, sender):
                SENDER.send(effect)
        else:
            SENDER.send(SimpleFade(color=Color(255, 255, 255)))


if __name__ == '__main__':
    try:
        gobject.threads_init()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        Listener()
        loop = gobject.MainLoop()
        loop.run()
    except KeyboardInterrupt:
        SENDER.stop()
