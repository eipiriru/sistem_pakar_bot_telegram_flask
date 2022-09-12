from flask import render_template, flash, redirect, url_for, session, request, jsonify
from sispak import app, db
from sispak.models import Gejala, Penyakit
from sispak.bot_config import TOKEN,URL
from sispak.routes import compute_next

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
        'Hi..! Selamat datang di MeowBot.\n'
        'Disini kamu bisa melakukan diagnosa awal pada penyakit yang diderita kucing kamu.\n\n'
        'Pilih menu /diagnosa untuk memulai diagnosa penyakit kucing kamu.\n'
        'Pilih menu /info untuk lebih kenal sama MeowBot.\n',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Pilih Menu'
        ),
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

def respond_diagnosa(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat_id = user.id
    msg_id = update.message.message_id
    userNew = UserNew(user.first_name)
    message = """
		Untuk proses diagnosa, tanggapi Pertanyaan yang muncul dengan menekan tombol YA / TIDAK yang tersedia, tekan /cancel untuk membatalkan proses diagnosa
	"""
    bot.sendMessage(chat_id=chat_id, text=message)
    bot.sendMessage(chat_id=chat_id, text="Mohon tunguu... \nSedang Memuat pertanyaan...")
    daftar_penyakit = Penyakit.query.all()
    daftar_gejala = Gejala.query.all()
    penyakit= []
    gejala = []
    for i in daftar_gejala:
        gejala.append(i.id)
    for i in daftar_penyakit:
        penyakit.append(i.id)
	
    kamus = {
		'penyakit': penyakit,
		'gejala':gejala,
	}
    results = compute_next(kamus)
    
    userNew.penyakit_ya = results['penyakit_yes']
    userNew.penyakit_tidak = results['penyakit_no']
    userNew.gejala_ya = results['gejala_yes']
    userNew.gejala_tidak = results['gejala_no']
    userNew.gejala_next = results['pertanyaan']
    
    reply_keyboard = [['YA', 'TIDAK']]
    
    user_dict[chat_id] = userNew
    
    update.message.reply_text(
        'Apakah kucing mengalami gejala **' + results['pertanyaan'] + '**',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='YA ATAU TIDAK'
        ),
    )
    
    return PROSES

def respond_proses_diagnosa(update: Update, context: CallbackContext) -> int:
	user = update.message.from_user
	chat_id = user.id
	msg_id = update.message.message_id
	userNew = user_dict[chat_id]
	text_chat = update.message.text

	if text_chat == 'YA':
		reply_keyboard = [['YA', 'TIDAK']]
		reply_keyboard1 = [['/mulai_diagnosa']['/info']]
		reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder='YA ATAU TIDAK')
		reply_markup1=ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=True, input_field_placeholder='PILIH MENU')
		kamus = {
			'penyakit': userNew.penyakit_ya,
			'gejala':userNew.gejala_ya,
		}
		update_kamus = compute_next(kamus)
		if update_kamus['message'] == 'belum':
			userNew.penyakit_ya = update_kamus['penyakit_yes']
			userNew.penyakit_tidak = update_kamus['penyakit_no']
			userNew.gejala_ya = update_kamus['gejala_yes']
			userNew.gejala_tidak = update_kamus['gejala_no']
			userNew.gejala_next = update_kamus['pertanyaan']
			update.message.reply_text(
                'Apakah kucing kamu mengalami gejala **' + update_kamus['pertanyaan'] + '**',
                reply_markup=reply_markup)
			return PROSES
		elif update_kamus['message'] == 'sudah':
			update.message.reply_text(
                'Berdasarkan hasil diagnosa MeowBot, kemungkinan kucing kamu mengalami penyakit' + update_kamus['pertanyaan'] + '.\n\n'
                '**Deskripsi Penyakit ' + update_kamus['pertanyaan'] + ':**\n'
                '' + update_kamus['deskripsi'] + '\n\n'
                '**Solusi yang dapat ditawarkan MeowBot untuk kucing kamu :**\n'
                '' + update_kamus['penanganan'] + '\n'
            )
			update.message.reply_text(
                'Semoga kucing kamu baik-baik saja..\n'
                'Terima kasih sudah menggunakanku',
                reply_markup=reply_markup1
            )
			return ConversationHandler.END
	elif text_chat == 'TIDAK':
		reply_keyboard = [['YA', 'TIDAK']]
		reply_keyboard1 = [['/mulai_diagnosa']['/info']]
		reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder='YA ATAU TIDAK')
		reply_markup1=ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=True, input_field_placeholder='PILIH MENU')
		kamus = {
			'penyakit': userNew.penyakit_ya,
			'gejala':userNew.gejala_ya,
		}
		update_kamus = compute_next(kamus)
		if update_kamus['message'] == 'belum':
			userNew.penyakit_ya = update_kamus['penyakit_yes']
			userNew.penyakit_tidak = update_kamus['penyakit_no']
			userNew.gejala_ya = update_kamus['gejala_yes']
			userNew.gejala_tidak = update_kamus['gejala_no']
			userNew.gejala_next = update_kamus['pertanyaan']
			update.message.reply_text(
                'Apakah kucing kamu mengalami gejala **' + update_kamus['pertanyaan'] + '**',
                reply_markup=reply_markup)
			return PROSES
		elif update_kamus['message'] == 'sudah':
			update.message.reply_text(
                'Berdasarkan hasil diagnosa MeowBot, kemungkinan kucing kamu mengalami penyakit' + update_kamus['pertanyaan'] + '.\n\n'
                '**Deskripsi Penyakit ' + update_kamus['pertanyaan'] + ':**\n'
                '' + update_kamus['deskripsi'] + '\n\n'
                '**Solusi yang dapat ditawarkan MeowBot untuk kucing kamu :**\n'
                '' + update_kamus['penanganan'] + '\n'
            )
			update.message.reply_text(
                'Semoga kucing kamu baik-baik saja..\n'
                'Terima kasih sudah menggunakanku',
                reply_markup=reply_markup1
            )
			return ConversationHandler.END

def respond_info(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['/penyakit', '/diagnosa']]

    penyakit = Penyakit.query.all()
    daftar_penyakit = ""
    for i in penyakit:
        daftar_penyakit = daftar_penyakit + i.penyakit + "\n"

    update.message.reply_text(
        'Hi..! Selamat datang di MeowBot.\n'
        'Kenalin aku MeowBot\n'
        'Disini kamu bisa melakukan diagnosa awal pada penyakit yang diderita kucing kamu.\n'
        'Tapi penyakit kucing yang dapat didiagnosa oleh MeowBot masih terbatas, karena MeowBot masih belajar!!\n'
        'Sementara ini penyakit kucing yang dapat didiagnosa oleh MeowBot, terbatas pada penyakit\n'
        '' + daftar_penyakit + '\n'
        'Perlu diingat, MeowBot hanya melakukan diagnosa dini pada penyakit kucing kamu, sehingga belum 100 persen akurat.\n'
        'Untuk informasi yang lebih akurat, kamu bisa membawa kucing kamu ke dokter hewan terdekat.\n',
    )
    update.message.reply_text(
        'Pilih menu /diagnosa untuk memulai diagnosa penyakit kucing kamu.\n'
        'Pilih menu /info untuk lebih kenal sama MeowBot.\n',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Pilih Menu'
        ),
    )

    return ConversationHandler.END

run_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

diagnosa_handler = ConversationHandler(
    entry_points=[CommandHandler('diagnosa', respond_diagnosa)],
    states={
        PROSES: [MessageHandler(Filters.regex('^(YA|TIDAK)$'), respond_proses_diagnosa)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

info_handler = ConversationHandler(
    entry_points=[CommandHandler('info', respond_info)],
    states={
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

dispatcher.add_handler(run_handler)
dispatcher.add_handler(diagnosa_handler)
dispatcher.add_handler(info_handler)

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