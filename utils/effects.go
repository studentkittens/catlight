package main

import (
	"fmt"
	"io"
	"math"
	"os/exec"
	"time"
)

type EffectQueue struct {
	StdInPipe io.Writer
}

func (q *EffectQueue) Push(e Effect) {
	c := e.ComposeEffect()
	for color := range c {
		colorValue := fmt.Sprintf("%d %d %d\n", color.R, color.G, color.B)
		q.StdInPipe.Write([]byte(colorValue))
	}
}

func CreateEffectQueue() (*EffectQueue, error) {
	cmd := exec.Command("catlight", "cat")
	stdinpipe, err := cmd.StdinPipe()
	if err != nil {
		return &EffectQueue{StdInPipe: nil}, err
	}
	return &EffectQueue{stdinpipe}, cmd.Start()
}

type SimpleColor struct {
	R, G, B uint8
}

type Effect interface {
	ComposeEffect() chan SimpleColor
}

type Properties struct {
	Delay  time.Duration
	Color  SimpleColor
	Repeat int
	Cancel bool
}

type FadeEffect struct {
	Properties
}

type FlashEffect struct {
	Properties
}

func (color *SimpleColor) ComposeEffect() chan SimpleColor {
	c := make(chan SimpleColor, 1)
	c <- SimpleColor{color.R, color.G, color.B}
	close(c)
	return c
}

func (effect *FlashEffect) ComposeEffect() chan SimpleColor {
	c := make(chan SimpleColor, 1)
	keepLooping := false
	if effect.Repeat <= 0 {
		keepLooping = true
	}
	go func() {
		for {
			if effect.Repeat <= 0 && !keepLooping {
				break
			}
			c <- effect.Color
			time.Sleep(effect.Delay)
			c <- SimpleColor{0, 0, 0}
			time.Sleep(effect.Delay)
			effect.Repeat--
		}
		close(c)
	}()
	return c
}

func max(r uint8, g uint8, b uint8) uint8 {
	max := r
	if max < g {
		max = g
	}
	if max < b {
		max = b
	}
	return max
}

func (effect *FadeEffect) ComposeEffect() chan SimpleColor {
	c := make(chan SimpleColor, 1)

	keepLooping := false
	if effect.Repeat <= 0 {
		keepLooping = true
	}

	max := max(effect.Color.R, effect.Color.B, effect.Color.G)
	go func() {
		for {

			if effect.Repeat <= 0 && !keepLooping {
				break
			}

			r := int(math.Floor(float64(effect.Color.R) / float64(max) * 100.0))
			g := int(math.Floor(float64(effect.Color.G) / float64(max) * 100.0))
			b := int(math.Floor(float64(effect.Color.B) / float64(max) * 100.0))

			for i := 0; i < int(max); i += 1 {
				c <- SimpleColor{uint8((i * r) / 100), uint8((i * g) / 100), uint8((i * b) / 100)}
				time.Sleep(effect.Delay)
			}

			for i := int(max - 1); i >= 0; i -= 1 {
				c <- SimpleColor{uint8((i * r) / 100), uint8((i * g) / 100), uint8((i * b) / 100)}
				time.Sleep(effect.Delay)
			}
			effect.Repeat--
		}
		close(c)
	}()
	return c
}

// func main() {
// 	q, err := CreateEffectQueue()
// 	if err != nil {
// 		fmt.Println(err)
//
// 	}
// 	//q.Push(&SimpleColor{0, 255, 0})
//
// 	q.Push(&FadeEffect{Properties{Delay: 4 * time.Millisecond, Color: SimpleColor{255, 77, 0}, Repeat: 3}})
// }
