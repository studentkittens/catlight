package main

import (
	"fmt"
	"math/rand"
	"time"
)

func randColor() SimpleColor {
	return SimpleColor{
		uint8(rand.Int()%256 + 30),
		uint8(rand.Int()%256 + 30),
		uint8(rand.Int()%256 + 30),
	}
}

func main() {
	queue, err := CreateEffectQueue()
	if err != nil {
		fmt.Println(err)
		return
	}

	lastColor := randColor()

	for {
		currColor := randColor()
		queue.Push(&BlendEffect{
			lastColor,
			currColor,
			time.Millisecond * 10000,
		})

		lastColor = currColor
	}
}
