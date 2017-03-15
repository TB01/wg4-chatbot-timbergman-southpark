#!/usr/bin/env python
#
# framework of the chatbot is based on:
# Gareth Dwyer's tutorial on:
# Building a Chatbot using Telegram and Python
# https://www.codementor.io/garethdwyer/building-a-telegram-bot-using-python-part-1-goi5fncay
# https://github.com/sixhobbits/python-telegram-tutorial
#
# uses assets crawled from 
#    http://southpark.wikia.com/wiki/South_Park_Archives
#
# South Park copyright info: 
#   http://southpark.cc.com/about/legal/terms-of-use
#
# for education purposes only

# ************************ IMPORTS ********************************

import json 
import requests
import time
import urllib
import config # for the chatbot token
import sys 
import traceback

try:
    from urllib.parse import quote_plus as pathname2url # python3
except ImportError: 
    from urllib import pathname2url as pathname2url # python2
try: 
    from urllib.parse import urlparse # python3
except ImportError: 
    from urlparse import urlparse # python2

# ************************ CONSTANTS ********************************

from MyModel import MyModel as Model

# create a config file, add a token variable with the chatbot token
# then import config
TOKEN = config.token 
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

pars = { # PARAMETERS for the chatbot model
    # paths to sqlite database files:
    'qdbname'   : 'SouthParkEpisodesDB.sqlite', # quotes database
    'sdbname'   : 'SouthParkEpisodesSummariesDB.sqlite', # summaries db
    # paths to corpus text files:
    'msumname'  : 'SouthParkEpisodeSummariesALL.txt', # episode summaries
    'mtitlename': 'SouthParkEpisodeTitlesALL.txt', # episode titles
    'mquotename': 'SouthParkEpisodeQuotesALL.txt', # ALL quotes
    # markov text generation:
    'usenlpformarkov': False, # use nlp pos tags for markov text generation
    'cartmanify': True, # do you want to give 'personality' to answers?
    # misc options:
    'debug'     : True, # display debug messages
}

# ************************ FUNCTIONS ********************************

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def respond(updates, model):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        (response,chat,reply_markup) = model.respond(text, chat)
        if response is not None:
            send_message(response, chat, reply_markup)

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def send_message(text, chat_id, reply_markup=None):
    print('response: ' + text[slice(0,56)].strip().replace('\n',' ') + '...')
    text = pathname2url(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

# ************************ MAIN ********************************

def main():
    model = Model(pars = pars)
    updates = None
    last_update_id = None
    print('start running chatbot')
    run = True
    while run:
        try:
            updates = get_updates(last_update_id)
            if len(updates["result"]) > 0:
                last_update_id = get_last_update_id(updates) + 1
                respond(updates, model)
            time.sleep(0.5)
        except Exception as e:
            print(type(e), e, e.args)
            traceback.print_exc(file=sys.stdout)
            run = False
    print('stopped running chatbot')

if __name__ == '__main__':
    main()
    sys.exit('ok doei <3')
