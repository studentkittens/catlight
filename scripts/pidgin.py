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
        'christoph@jabber.nullcat.de*': KaminFeuerDerLust(),
        'zwille@jabber.i-pobox.net': SimpleFade(color=Color(255, 0, 0)),
        'eddys@jabber.i-pobox.net': SimpleFade(color=Color(128, 0, 0)),
        '431575929': SimpleFade(color=Color(0, 255, 0)),
        '395752334': SimpleFade(color=Color(0, 0, 255))
}


class Listener:
    def __init__(self):
        self.__bus = dbus.SessionBus()
        self.__bus.add_signal_receiver(self.received_msg,
                dbus_interface="im.pidgin.purple.PurpleInterface",
                signal_name="ReceivedImMsg")

    def received_msg(self, account, sender, message, conversation, flags):
        effect = buddy_reactions.get(sender, SimpleFade())
        SENDER.send(effect)


if __name__ == '__main__':
    try:
        gobject.threads_init()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        Listener()
        loop = gobject.MainLoop()
        loop.run()
    except KeyboardInterrupt:
        SENDER.stop()
