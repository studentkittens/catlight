package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"time"
)

type Job struct {
	Id    int    `json:"id"`
	State string `json:"state"`
}

type Repository struct {
	Builds []Job `json:"builds"`
}

func (j Job) String() string {
	return fmt.Sprintf("Job(#%d: %s)", j.Id, j.State)
}

func (repo *Repository) IsNewer(other *Repository) bool {
	if repo == nil || len(repo.Builds) == 0 {
		return false
	}

	if other == nil || len(repo.Builds) == 0 {
		return true
	}

	return repo.Builds[0].State != other.Builds[0].State
}

var COLORS = map[string]SimpleColor{
	"passed":   SimpleColor{0, 255, 0},
	"created":  SimpleColor{0, 0, 255},
	"received": SimpleColor{255, 255, 0},
	"started":  SimpleColor{255, 255, 128},
	"errored":  SimpleColor{255, 0, 0},
	"failed":   SimpleColor{255, 0, 0},
}

func (repo *Repository) Visualize(queue *EffectQueue) {
	if len(repo.Builds) == 0 {
		return
	}

	state := repo.Builds[0].State
	color, ok := COLORS[state]

	fmt.Println("==> State changed to:", state)

	if !ok {
		fmt.Println("==> No such state:", state, "(assuming errored)")
		color = COLORS["errored"]
	}

	queue.Push(&FlashEffect{Properties{
		Delay:  250 * time.Millisecond,
		Color:  color,
		Repeat: 3,
	}})
	queue.Push(&color)
}

func DownloadRepo(user string, name string) ([]byte, error) {
	client := &http.Client{}

	url := "https://api.travis-ci.org/repos/%s/%s/builds"
	req, err := http.NewRequest("GET", fmt.Sprintf(url, user, name), nil)

	if err != nil {
		return nil, nil
	}

	req.Header.Add("Accept", "application/vnd.travis-ci.2+json")
	req.Header.Add("User-Agent", "catlight/0.0.1")
	if resp, err := client.Do(req); err == nil {
		defer resp.Body.Close()
		fmt.Println("GET", req.URL)
		return ioutil.ReadAll(resp.Body)
	} else {
		return nil, nil
	}
}

func ParseJson(data []byte) *Repository {
	repo := Repository{}
	if err := json.Unmarshal(data, &repo); err != nil {
		fmt.Println("Unable to parse json", err)
		return nil
	}

	return &repo
}

func NewRepo(user string, name string) *Repository {
	if data, err := DownloadRepo(user, name); err == nil {
		return ParseJson(data)
	}

	return nil
}

func main() {
	userPromise := flag.String("user", "sahib", "GitHub user")
	namePromise := flag.String("name", "rmlint", "GitHub repo name")
	flag.Parse()

	var newRepo *Repository = nil
	var oldRepo *Repository = nil

	queue, err := CreateEffectQueue()
	if err != nil {
		fmt.Println(err)
		return
	}

	sigs := make(chan os.Signal, 1)
	upds := make(chan bool, 1)
	signal.Notify(sigs, os.Interrupt)

	upds <- true

	for {
		select {
		case sig := <-sigs:
			fmt.Println("SIGNAL:", sig)
			// Can't use queue; catlight process was killed by SIGINT too.
			defer func() {
				cmd := exec.Command("catlight", "off")
				cmd.Run()
			}()
			return
		case <-upds:
			go func() {
				newRepo = NewRepo(*userPromise, *namePromise)
				if newRepo.IsNewer(oldRepo) {
					newRepo.Visualize(queue)
				}

				oldRepo = newRepo
				time.Sleep(5000 * time.Millisecond)
				upds <- true
			}()
		}
	}

}
