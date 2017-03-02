#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages with XKCD comics
# This program is dedicated to the public domain under the CC0 license.

from uuid import uuid4

import re

from telegram import InlineQueryResultArticle, InlineQueryResultPhoto, ParseMode, \
    InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging
from urllib.request import urlopen
import requests
import json
import codecs

# Enable time based logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text='Hello, I am an XKCD Inline bot. Mention me in your chats with the comic number that you want to reference and I\'ll provide the results.')


def shorten_url(long_url):
    response = requests.post('https://ptpb.pw/u', data={'c': long_url})
    url = response.headers.get('Location')
    return url


def getJSON(uri):
    reader = codecs.getreader("utf-8")
    base = "http://xkcd.com/"
    url = "http://xkcd.com/" + str(uri) + "/info.0.json"
    jsonurl = urlopen(url)
    jsonStr = json.load(reader(jsonurl))
    return jsonStr


def convertURL(query):
    text = getJSON(query)
    imgLink = text['img']
    return imgLink


def getAlt(query):
    text = getJSON(query)
    alt = text['alt']
    return alt


def getTitle(query):
    text = getJSON(query)
    title = text['safe_title']
    return title


def inlinequery(bot, update):
    comicTitle = ''
    query = update.inline_query.query
    results = list()
    if query == '' or ' ':
        comicTitle = 'Latest comic'
    else:
        comicTitle = 'xkcd:' + str(query)
    results.append(InlineQueryResultArticle(id=uuid4(),
                                            title=comicTitle,
                                            description=getAlt(query),
                                            thumb_url=convertURL(query),
                                            cache_time=15,
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Comic Link', 'https://xkcd.com/' + query)],[InlineKeyboardButton(
                                                'Explain XKCD', 'http://www.explainxkcd.com/wiki/index.php/' + query)]]),
                                            input_message_content=InputTextMessageContent('*Title:* ' + getTitle(query) + '\n*Alt:* ' + getAlt(query) +'\n[Image Link](' + convertURL(query) + ')',parse_mode='Markdown')))

    bot.answerInlineQuery(update.inline_query.id, results=results)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():

    with open('token.txt','r') as token:
        token_ = token.read().strip('\n') # Add your token to token.txt
    # Create the Updater and pass it your bot's token.
    updater = Updater(token_)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

# Run only if it is the main program, and not when it is referenced from some other code
if __name__ == '__main__':
    main()
