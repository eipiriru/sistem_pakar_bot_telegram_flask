from flask import render_template, flash, redirect, url_for, session, request, jsonify
from sispak import app, db
from sispak.models import Gejala, Penyakit, BotConfig

import re
import telegram
import json, requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

def get_token_bot():
    botconfig = BotConfig.query.all()
    if len(botconfig) > 0:
        botconfig = BotConfig.query.filter_by().first()
        url = "https://api.telegram.org/bot" + str(botconfig.token) +"/getMe"
        headers = {"Accept": "application/json"}
        response = requests.post(url, headers=headers)
        result = json.loads(response.text)
        if not result['ok']:
            pass
        else:
            return botconfig.token
    return "5298360325:AAGXkroxsanxc4QWPgb_vHQS-XPAp4yjUV0"

def get_url():
    return "https://testing-sispak.herokuapp.com"

global bot
global TOKEN
global updater
global dispatcher

TOKEN = get_token_bot()
URL = get_url()
bot = telegram.Bot(token=TOKEN)
updater = Updater(TOKEN)
dispatcher = updater.dispatcher

BIO, START, PROSES = range(3)

user_dict = {}

class UserNew:
	def __init__(self, name):
		self.name = name
		self.gejala_next = None
		self.penyakit_ya = None
		self.penyakit_tidak = None
		self.gejala_ya = None
		self.gejala_tidak = None
		self.bio = None

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
	update = telegram.Update.de_json(request.get_json(force=True), bot)

	updater.start_polling()

	chat_id = update.message.chat.id
	msg_id = update.message.message_id
	
	user = update.message.from_user
	print (user)
	chatNew_id = user.id
	userNew = UserNew(user.first_name)
	user_dict[chatNew_id] = userNew
	
	text = update.message.text.encode('utf-8').decode()
	
	if text == "/start":
		bot.sendMessage(chat_id=chat_id, text="Hello World", reply_to_message_id=msg_id)
		# respond_start(chat_id,msg_id,userNew)
	# elif text == "/help":
	# 	respond_help(chat_id,msg_id,user_dict)
	# elif text == "/siswa":
	# 	get_siswa(chat_id,msg_id)
	else:
		try:
			text = re.sub(r"\W", "_", text)
			url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
			# bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
			bot_msg = "You said in "+text
			bot.sendMessage(chat_id=chat_id, text=bot_msg, reply_to_message_id=msg_id)
		except Exception:
			# if things went wrong
			bot.sendMessage(chat_id=chat_id, text="There was a problem in the name you used, please enter different name", reply_to_message_id=msg_id)
	return 'ok'

@app.route('/bottelegram', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "Bot Telegram Active Successfully"
    else:
        return "Bot Telegram Failed"