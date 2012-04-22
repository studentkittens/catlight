#!/usr/bin/env python
import dbus, gobject, led_connection
from dbus.mainloop.glib import DBusGMainLoop


class Listener:
    def __init__(self):
        self.do_blink = False 
        self.stop_blink = False
        self.bus = dbus.SessionBus()
        self.register_signal(self.received_msg,"ReceivedImMsg")
        self.register_signal(self.conversation_updated,"ConversationUpdated")

    def register_signal(self,func,name):
        self.bus.add_signal_receiver(func, dbus_interface="im.pidgin.purple.PurpleInterface", signal_name=name)

    def received_msg(self,account, sender, message, conversation, flags):
        print(sender, "said:", message)
        led_connection.on()
        self.do_blink = True 

    def conversation_updated(self,conv,flag):
        print(conv,flag)
        if self.stop_blink:
            print("Jetzt sollte ich zu blinken aufhoeren?")
            led_connection.off()
            self.stop_blink = False

        if flag == 4 and self.do_blink:
            self.do_blink = False
            self.stop_blink = True


DBusGMainLoop(set_as_default=True)

l = Listener()

loop = gobject.MainLoop()
loop.run()
