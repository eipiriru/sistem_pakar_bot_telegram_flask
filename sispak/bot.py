from flask import render_template, flash, redirect, url_for, session, request, jsonify
from sispak import app, db
from sispak.models import Gejala, Penyakit
from sispak.bot_config import TOKEN,URL

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

global bot
global updater
global dispatcher

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

def respond_start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['/cancel', '/cancel']]

    update.message.reply_text(
        'Hi! This Pakar Bot. I will hold a conversation with you. '
        'Send /cancel to stop talking to me.\n\n'
        'Choose Menu?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
        ),
    )

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
	"""Cancels and ends the conversation."""
	reply_keyboard = ['/start']
	user = update.message.from_user
	update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
        )
    )
	return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', respond_start)],
    states={
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

dispatcher.add_handler(conv_handler)

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
	update = telegram.Update.de_json(request.get_json(force=True), bot)
	updater.start_polling()
	return 'ok'

@app.route('/bottelegram', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "Bot Telegram Active Successfully"
    else:
        return "Bot Telegram Failed"