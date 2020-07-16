package main

import (
	"log"
	"os"
	"strconv"

	"github.com/go-telegram-bot-api/telegram-bot-api"
	"github.com/thunderbottom/xkcd/xkcd"
)

const (
	DEBUG = false
	TG_UPDATE_TIMEOUT = 60
)

var (
	TOKEN = os.Getenv("TOKEN")
)

func main() {
	bot, err := tgbotapi.NewBotAPI(TOKEN)
	if err != nil {
		log.Panic("Error fetching TOKEN from environment: ", err.Error())
	}

	bot.Debug = DEBUG

	log.Printf("Authorized as @%s", bot.Self.UserName)

	u := tgbotapi.NewUpdate(0)
	u.Timeout = TG_UPDATE_TIMEOUT

	updates, err := bot.GetUpdatesChan(u)

	for update := range updates {
		if update.Message != nil {
			log.Printf("Message from: @%s\nMessage: %s",
				update.Message.From.UserName, update.Message.Text)
		} else if update.InlineQuery != nil {
			log.Printf("Inline Query from: @%s\nMessage: %s",
					update.InlineQuery.From.UserName, update.InlineQuery.Query)

			comic_number, err := strconv.Atoi(update.InlineQuery.Query)
			if err != nil {
				comic_number = 0
			}
			if comic, err := xkcd.GetComic(comic_number); err == nil {
				image := tgbotapi.NewInlineQueryResultPhotoWithThumb(
						update.InlineQuery.ID,
						comic.Image,
						comic.Image)
				image.Caption = comic.AltText
				reply := tgbotapi.InlineConfig{
					InlineQueryID: image.ID,
					Results: []interface{}{image},
					CacheTime: 0,
				}
				if _, err := bot.AnswerInlineQuery(reply); err != nil {
					log.Println("Failed to answer query: ", err.Error())
					continue
				}
			}
		}
	}
}
