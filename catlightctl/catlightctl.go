package main

import (
	"flag"
	"fmt"
	"log"
	"net"
	"os"
)

func main() {
	portFlag := flag.Int("port", 3333, "Port of catlightd")
	hostFlag := flag.String("host", "localhost", "Host of catlightd")
	flag.Parse()

	conn, err := net.Dial("tcp", fmt.Sprintf("%s:%d", *hostFlag, *portFlag))
	if err != nil {
		log.Fatalf("Unable to connect to `catlightd`: %v", err)
		os.Exit(1)
	}

	defer conn.Close()

	for _, effectSpec := range flag.Args() {
		effectLine := effectSpec + "\n"
		if _, err := conn.Write([]byte(effectLine)); err != nil {
			log.Fatalf("Cannot send effect `%s`: %v", effectSpec, err)
		}
	}
}
