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

GENDER, PHOTO, LOCATION, BIO, START, PROSES = range(6)

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

def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation"""
    reply_keyboard = [['/mulai_diagnosa']['/info']]

    update.message.reply_text(
        'Hi..! Selamat datang di **MeowBot**.\n'
        'Disini kamu bisa melakukan diagnosa awal pada penyakit yang diderita kucing kamu.\n\n'
        'Pilih menu /diagnosa untuk memulai diagnosa penyakit kucing kamu.\n'
        'Pilih menu /info untuk lebih kenal sama MeowBot.\n',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Pilih Menu'
        ),
    )

    return ConversationHandler.END


def gender(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    print (user)
    chat_id = user.id
    userNew = UserNew(user.first_name)
    userNew.sex = update.message.text
    user_dict[chat_id] = userNew
    update.message.reply_text(
        'I see! Please send me a photo of yourself, '
        'so I know what you look like, or send /skip if you don\'t want to.',
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


def photo(update: Update, context: CallbackContext) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    update.message.reply_text(
        'Gorgeous! Now, send me your location please, or send /skip if you don\'t want to.'
    )

    return LOCATION


def skip_photo(update: Update, context: CallbackContext) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    update.message.reply_text(
        'I bet you look great! Now, send me your location please, or send /skip.'
    )

    return LOCATION


def location(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    update.message.reply_text(
        'Maybe I can visit you sometime! At last, tell me something about yourself.'
    )

    return BIO


def skip_location(update: Update, context: CallbackContext) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    update.message.reply_text(
        'You seem a bit paranoid! At last, tell me something about yourself.'
    )

    return BIO


def bio(update: Update, context: CallbackContext) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    chat_id = user.id
    userNew = user_dict[chat_id]
    userNew.bio = update.message.text
    update.message.reply_text('Thank you ' + userNew.name + '! You a great ' + userNew.sex + 'I hope we can talk again some day.')

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
	"""Cancels and ends the conversation."""
	reply_keyboard = [['/mulai_diagnosa']['/info']]
	user = update.message.from_user
	update.message.reply_text(
        'Okee..', reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
        )
    )
	return ConversationHandler.END

run_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

dispatcher.add_handler(run_handler)

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