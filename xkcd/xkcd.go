package xkcd

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

const (
	XKCD_URL = "https://xkcd.com/%d/info.0.json"
	CURRENT_COMIC_URL = "https://xkcd.com/info.0.json"
)

type Comic struct {
	AltText string `json:"alt"`
	Day string `json:"day"`
	Image string `json:"img"`
	Link string `json:"link"`
	Month string `json:"month"`
	News string `json:"news"`
	Number int `json:"num"`
	SafeTitle string `json:"safe_title"`
	Title string `json:"title"`
	Transcript string `json:"transcript"`
	Year string `json:"year"`
}

func GetComic(number int) (*Comic, error) {
	comic_url := CURRENT_COMIC_URL
	if number > 0 {
		comic_url = fmt.Sprintf(XKCD_URL, number)
	}

	response, err := http.Get(comic_url)
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()

	body, err := ioutil.ReadAll(response.Body)
	if err != nil {
		return nil, err
	}

	var comic Comic
	err = json.Unmarshal(body, &comic)
	if err != nil {
		return nil, err
	}

	return &comic, nil
}
