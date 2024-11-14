package main

import (
	"os"

	"messages/app_messages"
)

func main() {
	dat, _ := os.Open("./vec3.msg")
	defer dat.Close()
	msg := app_messages.Vector3MessageFromBytes(dat)
	if msg.X == 1.0 && msg.Y == 4096.1234 && msg.Z < 0.0 {
		print("Ready to go!\n")
	}
}
