from flask import render_template, flash, redirect, url_for, session, request, jsonify
from sispak import app, db
from sispak.models import Gejala, Penyakit, UserTelegram, HistoryDiagnosa, ProsesDiagnosa
from sispak.bot_config import TOKEN, URL

from datetime import datetime

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

START, PROSES, REGIS, CHANGENAME = range(4)

user_dict = {}


class UserNew:
    def __init__(self, name):
        self.name = name
        self.riwayat_id = None
        self.gejala_before = None
        self.seq = None
        self.gejala_next = None
        self.penyakit_ya = None
        self.penyakit_tidak = None
        self.gejala_ya = None
        self.gejala_tidak = None

def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation"""
    reply_keyboard = [['/diagnosa'],['/info','/change_name']]
    user = update.message.from_user
    print (user)
    user_telegram = UserTelegram.query.filter(UserTelegram.id_bot == user['id']).first()
    if user_telegram:
        user_telegram = UserTelegram.query.filter(UserTelegram.id_bot == user['id']).first()
        update.message.reply_text(
            'Hai {}! Selamat datang kembali di MeowBot.\n'
            'Disini kamu bisa melakukan diagnosa awal pada penyakit yang diderita kucing kamu.\n\n'
            'Pilih menu /diagnosa untuk memulai diagnosa penyakit kucing kamu.\n'
            'Pilih menu /info untuk lebih kenal sama MeowBot.\n'.format(user_telegram.name),
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder='Pilih Menu'
            ),
        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            'Hai..! Selamat datang di MeowBot.\n'
            'Boleh kenalan dulu. Aku bisa panggil kamu siapa?\n\n'
        )

        return REGIS

def regis(update: Update, context: CallbackContext) -> int:
    namanya = update.message.text
    user = update.message.from_user
    print (user)
    if user.username:
        create_user = UserTelegram(id_bot=user['id'], username=user['username'], name=namanya)
    else:
        create_user = UserTelegram(id_bot=user['id'], name=namanya)
    db.session.add(create_user)
    db.session.commit()

    reply_keyboard = [['/diagnosa'],['/info','/change_name']]
    update.message.reply_text(
        'Hai {}!\n'
        'Disini kamu bisa melakukan diagnosa awal pada penyakit yang diderita kucing kamu.\n\n'
        'Pilih menu /diagnosa untuk memulai diagnosa penyakit kucing kamu.\n'
        'Pilih menu /info untuk lebih kenal sama MeowBot.\n'.format(namanya),
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Pilih Menu'
        ),
    )
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
	"""Cancels and ends the conversation."""
	reply_keyboard = [['/diagnosa'],['/info','/change_name']]
	update.message.reply_text(
        'Okee..', reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
        )
    )
	return ConversationHandler.END

def compute_next(kamus, interupt=False):
    if interupt:
        return process_compute_interupt(kamus, interupt)
    else:
        return process_compute(kamus, interupt)

def process_compute_interupt(kamus, interupt=False):
    penyakit_yes = []
    penyakit_no = []
    gejala_yes = []
    gejala_no = []
    deskripsi = "belum"
    solusi = "belum"
    pertanyaan = "Maaf terdapat kesalahan tidak dapat mendeteksi penyakit"
    message = "interupt"
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

def process_compute(kamus, interupt=False):
    mentah_penyakit = kamus['penyakit']
    mentah_gejala = kamus['gejala']
    gejala = Gejala.query.filter(Gejala.id.in_(mentah_gejala)).all()
    panjang_penyakit = len(mentah_penyakit)
    g_max = 0
    item = 0

    if panjang_penyakit == 1:
        penyakit_yes = []
        penyakit_no = []
        gejala_yes = []
        gejala_no = []
        penyakit = Penyakit.query.filter(Penyakit.id == mentah_penyakit[0]).first()
        pertanyaan = penyakit.penyakit
        message = "sudah"
        deskripsi = penyakit.deskripsi
        solusi = penyakit.penanganan
        image = penyakit.id
        results = {
            'penyakit_yes' : penyakit_yes,
            'penyakit_no' : penyakit_no,
            'gejala_yes' : gejala_yes,
            'gejala_no' : gejala_no,
            'pertanyaan' : pertanyaan,
            'message' : message,
            'deskripsi' : deskripsi,
            'solusi': solusi,
            'image':image

        }
        return results

    for i in gejala:
        if item == 0:
            a = Gejala.query.filter(Gejala.id == i.id).first()
            a_penyakit = [i.id for i in a.penyakit]
            count_a = 0
            for j in mentah_penyakit:
                if j in a_penyakit:
                    count_a = count_a + 1

            if count_a == panjang_penyakit:
                continue
            g_max = i.id
            item = item + 1
        else:
            a = Gejala.query.filter(Gejala.id == g_max).first()
            a_penyakit = [ i.id for i in a.penyakit]
            count_a = 0
            for j in mentah_penyakit:
                if j in a_penyakit:
                    count_a = count_a + 1
            b = Gejala.query.filter(Gejala.id == i.id).first()
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
    gejala_yes = []
    gejala_no = []
    pertanyaan = "belum"
    message = "belum"
    deskripsi = "belum"
    solusi = "belum"
    image = ""

    if g_max != 0:
        next_gejala = Gejala.query.filter(Gejala.id == g_max).first()
        penyakit_in_next_gejala = [ i.id for i in next_gejala.penyakit ]
        for i in mentah_penyakit:
            if i in penyakit_in_next_gejala:
                penyakit_yes.append(i)
            else:
                penyakit_no.append(i)

        mentah_gejala.remove(g_max)
        sisa_gejala = Gejala.query.filter(Gejala.id.in_(mentah_gejala)).all()

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
            penyakit = Penyakit.query.filter(Penyakit.id == mentah_penyakit[0]).first()
            pertanyaan = penyakit.penyakit
            message = "sudah"
            deskripsi = penyakit.deskripsi
            solusi = penyakit.penanganan
            image = penyakit.id
        results = {
            'penyakit_yes' : penyakit_yes,
            'penyakit_no' : penyakit_no,
            'gejala_yes' : gejala_yes,
            'gejala_no' : gejala_no,
            'pertanyaan' : pertanyaan,
            'message' : message,
            'deskripsi' : deskripsi,
            'solusi': solusi,
            'image':image
        }
    else:
        pertanyaan = "Tidak dapat mendeteksi penyakit"
        message = "nothing"
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
    print (user)
    user_telegram = UserTelegram.query.filter(UserTelegram.id_bot == user['id']).first()
    if not user_telegram:
        update.message.reply_text(
            'Hai..! Selamat datang di MeowBot.\n'
            'Boleh kenalan dulu. Aku bisa panggil kamu siapa?\n\n',
        )

        return REGIS

    chat_id = user['id']
    msg_id = update.message.message_id
    create_riwayat = HistoryDiagnosa(usertelegram_id=user_telegram.id, tanggal=datetime.now())
    db.session.add(create_riwayat)
    db.session.commit()

    userNew = UserNew(user.first_name)
    userNew.riwayat_id = create_riwayat.id
    userNew.seq = 1
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
    chat_id = user['id']
    msg_id = update.message.message_id
    userNew = user_dict[chat_id]
    text_chat = update.message.text

    create_proses = ProsesDiagnosa(history_id=userNew.riwayat_id, seq=userNew.seq, gejala=userNew.gejala_next, respon=text_chat)
    db.session.add(create_proses)
    db.session.commit()

    if text_chat == 'YA':
        reply_keyboard = [['YA', 'TIDAK']]
        reply_keyboard1 = [['/diagnosa'],['/info','/change_name']]
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
            userNew.seq = userNew.seq + 1
            update.message.reply_text(
                'Apakah kucing kamu mengalami gejala **' + update_kamus['pertanyaan'] + '**',
                reply_markup=reply_markup)
            return PROSES
        elif update_kamus['message'] == 'nothing':
            history = HistoryDiagnosa.query.get(userNew.riwayat_id)
            history.hasil = "Tidak dapat mendeteksi penyakit"
            db.session.commit()

            update.message.reply_text(
                'Mohon maaf, MeowBot tidak dapat menemukan penyakit yang diderita kucing kamu :(\n\n'
                'MeowBot akan belajar lebih giat lagi..'
            )
            update.message.reply_text(
                'Semoga kucing kamu baik-baik saja..\n',
                reply_markup=reply_markup1
            )
            return ConversationHandler.END
        elif update_kamus['message'] == 'sudah':
            penyakit = Penyakit.query.filter(Penyakit.id == update_kamus['image']).first()
            if len(penyakit.gejala) > 0:
                if penyakit.data:
                    update.message.reply_photo(photo=penyakit.data)

                history = HistoryDiagnosa.query.get(userNew.riwayat_id)
                history.hasil = update_kamus['pertanyaan']
                db.session.commit()

                update.message.reply_text(
                    'Berdasarkan hasil diagnosa MeowBot, kemungkinan kucing kamu mengalami penyakit ' + update_kamus['pertanyaan'] + '.\n\n'
                    '**Deskripsi Penyakit ' + update_kamus['pertanyaan'] + ':\n'
                    '' + update_kamus['deskripsi'] + '\n\n'
                    '**Solusi yang ditawarkan MeowBot untuk kucing kamu :\n'
                    '' + update_kamus['solusi'] + '\n'
                )
                update.message.reply_text(
                    'Semoga kucing kamu baik-baik saja..\n'
                    'Terima kasih sudah menggunakanku',
                    reply_markup=reply_markup1
                )
            else:
                history = HistoryDiagnosa.query.get(userNew.riwayat_id)
                history.hasil = "Tidak terdeteksi penyakit"
                db.session.commit()

                update.message.reply_text(
                    'Kucing kamu tidak terdeteksi penyakit\n'
                    'Kucing kamu baik-baik saja',
                    reply_markup=reply_markup1
                )
            return ConversationHandler.END
    elif text_chat == 'TIDAK':
        reply_keyboard = [['YA', 'TIDAK']]
        reply_keyboard1 = [['/diagnosa'],['/info','/change_name']]
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
            userNew.seq = userNew.seq + 1
            update.message.reply_text(
                'Apakah kucing kamu mengalami gejala **' + update_kamus['pertanyaan'] + '**',
                reply_markup=reply_markup)
            return PROSES
        elif update_kamus['message'] == 'nothing':
            history = HistoryDiagnosa.query.get(userNew.riwayat_id)
            history.hasil = "Tidak dapat mendeteksi penyakit"
            db.session.commit()

            update.message.reply_text(
                'Mohon maaf, MeowBot tidak dapat menemukan penyakit yang diderita kucing kamu :(\n\n'
                'MeowBot akan belajar lebih giat lagi..'
            )
            update.message.reply_text(
                'Semoga kucing kamu baik-baik saja..\n',
                reply_markup=reply_markup1
            )
            return ConversationHandler.END
        elif update_kamus['message'] == 'sudah':
            penyakit = Penyakit.query.filter(Penyakit.id == update_kamus['image']).first()
            if len(penyakit.gejala) > 0:
                if penyakit.data:
                    update.message.reply_photo(photo=penyakit.data)

                history = HistoryDiagnosa.query.get(userNew.riwayat_id)
                history.hasil = update_kamus['pertanyaan']
                db.session.commit()

                update.message.reply_text(
                    'Berdasarkan hasil diagnosa MeowBot, kemungkinan kucing kamu mengalami penyakit ' + update_kamus['pertanyaan'] + '.\n\n'
                    '**Deskripsi Penyakit ' + update_kamus['pertanyaan'] + ':\n'
                    '' + update_kamus['deskripsi'] + '\n\n'
                    '**Solusi yang ditawarkan MeowBot untuk kucing kamu :\n'
                    '' + update_kamus['solusi'] + '\n'
                )
                update.message.reply_text(
                    'Semoga kucing kamu baik-baik saja..\n'
                    'Terima kasih sudah menggunakanku',
                    reply_markup=reply_markup1
                )
            else:
                history = HistoryDiagnosa.query.get(userNew.riwayat_id)
                history.hasil = "Tidak terdeteksi penyakit"
                db.session.commit()

                update.message.reply_text(
                    'Kucing kamu tidak terdeteksi penyakit\n'
                    'Kucing kamu baik-baik saja',
                    reply_markup=reply_markup1
                )
            return ConversationHandler.END

def respond_info(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['/diagnosa'],['/info','/change_name']]

    penyakit = Penyakit.query.all()
    daftar_penyakit = ""
    for i in penyakit:
        if len(i.gejala) > 0:
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

def respond_change_name(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_telegram = UserTelegram.query.filter(UserTelegram.id_bot == user['id']).first()
    if not user_telegram:
        update.message.reply_text(
            'Hai..! Selamat datang di MeowBot.\n'
            'Boleh kenalan dulu. Aku bisa panggil kamu siapa?\n\n',
        )

        return REGIS
    update.message.reply_text(
        'Hai.. {}! Kamu mau Aku panggil apa?\n'.format(user_telegram.name)
    )

    return CHANGENAME

def respond_commit_change_name(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['/diagnosa'],['/info','/change_name']]
    namanya = update.message.text
    user = update.message.from_user
    user_telegram = UserTelegram.query.filter(UserTelegram.id_bot == user['id']).first()
    user_telegram.name = namanya
    db.session.commit()
    update.message.reply_text(
        'Oke-okeee, mulai sekarang Aku akan manggil kamu {} :)'.format(namanya),
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Pilih Menu'
        ),
    )

    return ConversationHandler.END

run_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        REGIS: [MessageHandler(Filters.text & ~Filters.command, regis)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

diagnosa_handler = ConversationHandler(
    entry_points=[CommandHandler('diagnosa', respond_diagnosa)],
    states={
        PROSES: [MessageHandler(Filters.regex('^(YA|TIDAK)$'), respond_proses_diagnosa)],
        REGIS: [MessageHandler(Filters.text & ~Filters.command, regis)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

info_handler = ConversationHandler(
    entry_points=[CommandHandler('info', respond_info)],
    states={
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

change_nama_panggilan = ConversationHandler(
    entry_points=[CommandHandler('change_name', respond_change_name)],
    states={
        CHANGENAME: [MessageHandler(Filters.text & ~Filters.command, respond_commit_change_name)],
        REGIS: [MessageHandler(Filters.text & ~Filters.command, regis)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

dispatcher.add_handler(run_handler)
dispatcher.add_handler(diagnosa_handler)
dispatcher.add_handler(info_handler)
dispatcher.add_handler(change_nama_panggilan)

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
	update = telegram.Update.de_json(request.get_json(force=True), bot)
# 	bot.sendMessage(chat_id=update.message.chat_id, text='Hello, there')
	dispatcher.process_update(update)
	# updater.start_polling()
	return 'ok'

@app.route('/setbottelegram', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "Webhoook for Bot Telegram is Active"
    else:
        return "Bot Telegram Failed"