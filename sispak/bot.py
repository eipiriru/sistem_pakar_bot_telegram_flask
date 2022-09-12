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
    reply_keyboard = [['/diagnosa'],['/info']]

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
	reply_keyboard = [['/diagnosa'],['/info']]
	user = update.message.from_user
	update.message.reply_text(
        'Okee..', reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
        )
    )
	return ConversationHandler.END

def compute_next(kamus):
    mentah_penyakit = kamus['penyakit']
    mentah_gejala = kamus['gejala']
    gejala = Gejala.query.filter(Gejala.id.in_(mentah_gejala)).all()
    panjang_penyakit = len(mentah_penyakit)
    g_max = 0
    item = 0
    for i in gejala:
        c = Gejala.query.filter(Gejala.id == i.id).one()
        print (c.gejala)
        print (len(c.penyakit))
        if item == 0:
            a = Gejala.query.filter(Gejala.id == i.id).one()
            if len(a.penyakit) == panjang_penyakit:
                continue
            g_max = i.id
            item = item + 1
        else:
            a = Gejala.query.filter(Gejala.id == g_max).one()
            a_penyakit = [ i.id for i in a.penyakit]
            count_a = 0
            for j in mentah_penyakit:
                if j in a_penyakit:
                    count_a = count_a + 1
            b = Gejala.query.filter(Gejala.id == i.id).one()
            b_penyakit = [ i.id for i in b.penyakit]
            count_b = 0
            for j in mentah_penyakit:
                if j in b_penyakit:
                    count_b = count_b + 1

            if count_b < panjang_penyakit:
                if count_a < count_b:
                    g_max = b.id
            item = item + 1
        
    penyakit_yes = []
    penyakit_no = []
    
    next_gejala = Gejala.query.filter(Gejala.id == g_max).one()
    penyakit_in_next_gejala = [ i.id for i in next_gejala.penyakit ]
    for i in mentah_penyakit:
        if i in penyakit_in_next_gejala:
            penyakit_yes.append(i)
        else:
            penyakit_no.append(i)
            
    mentah_gejala.remove(g_max)
    sisa_gejala = Gejala.query.filter(Gejala.id.in_(mentah_gejala)).all()
    
    gejala_yes = []
    gejala_no = []
	
    for i in sisa_gejala:
        for j in i.penyakit:
            if j in next_gejala.penyakit:
                gejala_yes.append(i.id)
                break

    for i in sisa_gejala:
        for j in i.penyakit:
            if j not in next_gejala.penyakit:
                gejala_no.append(i.id)
                break

    pertanyaan = next_gejala.gejala
    message = "belum"
    deskripsi = "belum"
    solusi = "belum"
    if len(mentah_penyakit) == 1:
        penyakit = Penyakit.query.filter(Penyakit.id == mentah_penyakit[0]).one()
        pertanyaan = penyakit.penyakit
        message = "sudah"
        deskripsi = penyakit.deskripsi
        solusi = penyakit.penanganan
    results = {
		'penyakit_yes' : penyakit_yes,
		'penyakit_no' : penyakit_no,
		'gejala_yes' : gejala_yes,
		'gejala_no' : gejala_no,
		'pertanyaan' : pertanyaan,
		'message' : message,
        'deskripsi' : deskripsi,
        'solusi' : solusi,
	}
    return results

def respond_diagnosa(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat_id = user.id
    msg_id = update.message.message_id
    userNew = UserNew(user.first_name)
    message = """
		Untuk proses diagnosa, tanggapi Pertanyaan yang muncul dengan menekan tombol YA / TIDAK yang tersedia, tekan /cancel untuk membatalkan proses diagnosa
	"""
    bot.sendMessage(chat_id=chat_id, text=message)
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
		reply_keyboard1 = [['/diagnosa'],['/info']]
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
                'Berdasarkan hasil diagnosa MeowBot, kemungkinan kucing kamu mengalami penyakit ' + update_kamus['pertanyaan'] + '.\n\n'
                '**Deskripsi Penyakit ' + update_kamus['pertanyaan'] + ':**\n'
                '' + update_kamus['deskripsi'] + '\n\n'
                '**Solusi yang dapat ditawarkan MeowBot untuk kucing kamu :**\n'
                '' + update_kamus['solusi'] + '\n'
            )
			update.message.reply_text(
                'Semoga kucing kamu baik-baik saja..\n'
                'Terima kasih sudah menggunakanku',
                reply_markup=reply_markup1
            )
			return ConversationHandler.END
	elif text_chat == 'TIDAK':
		reply_keyboard = [['YA', 'TIDAK']]
		reply_keyboard1 = [['/diagnosa'],['/info']]
		reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder='YA ATAU TIDAK')
		reply_markup1=ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=True, input_field_placeholder='PILIH MENU')
		kamus = {
			'penyakit': userNew.penyakit_tidak,
			'gejala':userNew.gejala_tidak,
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
                '' + update_kamus['solusi'] + '\n'
            )
			update.message.reply_text(
                'Semoga kucing kamu baik-baik saja..\n'
                'Terima kasih sudah menggunakanku',
                reply_markup=reply_markup1
            )
			return ConversationHandler.END

def respond_info(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['/diagnosa'],['/info']]

    penyakit = Penyakit.query.all()
    daftar_penyakit = ""
    for i in penyakit:
        daftar_penyakit = daftar_penyakit + i.penyakit + "\n"

    update.message.reply_text(
        'Hi..! Selamat datang di MeowBot.\n'
        'Kenalin aku MeowBot\n'
        'Disini kamu bisa melakukan diagnosa awal pada penyakit yang diderita kucing kamu.\n\n'
        'Tapi penyakit kucing yang dapat didiagnosa oleh MeowBot masih terbatas, karena MeowBot masih belajar\n\n'
        'Sementara ini penyakit kucing yang dapat didiagnosa oleh MeowBot, terbatas pada penyakit\n'
        '' + daftar_penyakit + '\n'
        '\nPerlu diingat, MeowBot hanya melakukan diagnosa dini pada penyakit kucing kamu, sehingga belum 100 persen akurat.\n\n'
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