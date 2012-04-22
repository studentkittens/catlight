#!/usr/bin/env python
import dbus, gobject, dbus.mainloop.glib
import effects
import time

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

class Listener:
    def __init__(self):
        self.bus = dbus.SessionBus()
        self.register_signal(self.received_msg,"ReceivedImMsg")
        self.register_signal(self.conversation_updated,"ConversationUpdated")
        self.msgtime = time.time()
        self.effect  = None

    def register_signal(self,func,name):
        self.bus.add_signal_receiver(func, dbus_interface="im.pidgin.purple.PurpleInterface", signal_name=name)

    def received_msg(self,account, sender, message, conversation, flags):
        print(str(sender) + " said: " + str(message))
        self.effect = effects.Repeater({
            'effects' : [effects.HerrchenFade()],
            'times'   : 1
            }).start() # Returns immediately
        self.msgtime = time.time()

    def conversation_updated(self,conv,flag):
        if flag == 4 and 1 < (time.time() - self.msgtime):
            if self.effect != None:
                self.effect.kill()
            self.msgtime = time.time()


l = Listener()
loop = gobject.MainLoop()
loop.run()
