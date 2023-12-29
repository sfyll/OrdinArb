package main

import (
	"log"

	"github.com/zeromq/goczmq"
)

const SOCKET_ADDRESS = "tcp://*:28332"

func main() {
	// Create a router socket and bind it to port 5555.
	router, err := goczmq.NewRouter(SOCKET_ADDRESS)
	if err != nil {
		log.Fatal(err)
	}
	defer router.Destroy()

	for {
		if request, err := router.RecvMessage(); err != nil {
			log.Fatal(err)
		} else {
			log.Printf("router received '%s' from '%v'", request[1], request[0])
		}
	}

}
