package main

import (
	"fmt"
	"github.com/godbus/dbus"
	"os"
	"strings"
)

func ConnectPidginReceivedImMsgSignal() chan *dbus.Signal {

	conn, err := dbus.SessionBus()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Failed to connect to session bus:", err)
		os.Exit(1)
	}

	call := conn.BusObject().Call("org.freedesktop.DBus.AddMatch", 0, "interface='im.pidgin.purple.PurpleInterface', path='/im/pidgin/purple/PurpleObject', type='signal', member='ReceivedImMsg'")
	if call.Err != nil {
		fmt.Fprintln(os.Stderr, "Failed to add match:", call.Err)
		os.Exit(1)
	}

	c := make(chan *dbus.Signal, 10)
	conn.Signal(c)
	return c
}

func main() {
	c := ConnectPidginReceivedImMsgSignal()
	for v := range c {
		name := fmt.Sprintf("%s", v.Body[1:2])
		if strings.Contains(name, "christoph@jabber.nullcat.de") {
			fmt.Println("kitteh")
		} else {
			fmt.Println("someone else.")
		}
	}

}
