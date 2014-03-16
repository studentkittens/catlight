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


default_reaction = SimpleFade(speed=0.6, color=Color(171, 243, 15))

# Actual uIDs are used, not aliases
buddy_reactions = {
    r'sahib.*': SimpleFade(speed=0.6, color=Color(255, 0, 255))
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
            if default_reaction:
                SENDER.send(default_reaction)


if __name__ == '__main__':
    SENDER.send(Color(0,0,0));
    try:
        gobject.threads_init()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        Listener()
        loop = gobject.MainLoop()
        loop.run()
    except KeyboardInterrupt:
        SENDER.stop()
