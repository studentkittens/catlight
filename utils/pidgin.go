package main

import (
	"fmt"
	"os"
	"time"

	"github.com/godbus/dbus"
)

func ConnectPidginReceivedImMsgSignal() chan *dbus.Signal {

	conn, err := dbus.SessionBus()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Failed to connect to session bus:", err)
		os.Exit(1)
	}

	call := conn.BusObject().Call(
		"org.freedesktop.DBus.AddMatch",
		0,
		"interface='im.pidgin.purple.PurpleInterface', path='/im/pidgin/purple/PurpleObject', type='signal', member='ReceivedImMsg'",
	)

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
	q, err := CreateEffectQueue()
	if err != nil {
		fmt.Println(err)
		return
	}

	for range c {
		// name := fmt.Sprintf("%s", v.Body[1:2])
		q.Push(&BlendEffect{
			SimpleColor{255, 0, 0},
			SimpleColor{0, 0, 255},
			time.Millisecond * 5000,
		})
		q.Push(&BlendEffect{
			SimpleColor{0, 0, 255},
			SimpleColor{0, 0, 0},
			time.Millisecond * 2000,
		})
	}
}
