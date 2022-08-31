from flask import render_template, flash, redirect, url_for, session, request, jsonify
from sispak import app, db
from sispak.models import Gejala, Penyakit

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
    # botconfig = BotConfig.query.all()
    # if len(botconfig) > 0:
    #     botconfig = BotConfig.query.filter_by().first()
    #     url = "https://api.telegram.org/bot" + str(botconfig.token) +"/getMe"
    #     headers = {"Accept": "application/json"}
    #     response = requests.post(url, headers=headers)
    #     result = json.loads(response.text)
    #     if not result['ok']:
    #         pass
    #     else:
    #         return botconfig.token
    return "5636164555:AAGLqDncfNNRDxYQTjZ6DkSP-z9fdanzHas"

def get_url():
    return "https://testing-ta.herokuapp.com"

TOKEN = get_token_bot()
URL = get_url()