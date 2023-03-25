from datetime import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Dispatcher
from deta import Deta
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import httpx

TOKEN = os.environ['TOKEN']
ADMIN_ID = [1697562512]

WELCOME_MESSAGE = """Aselamaleykum {name}

Welcome to the Quran Bot you can use this bot to listen to the recitation of the Quran with different reciters.

Please click on the button below to choose the reciter you want to listen to.

Join my channel https://t.me/codewizme to learn more about me and my projects.
"""

FILE_TOO_LARGE = '''File is too large to update. Due to telegram limitations. We are working on it to fix the issue. 

In the meantime you can download the file that might be less than 50mb.

To download the file click on the button below.
'''


class TelegramWebhook(BaseModel):
    update_id: int
    message: Optional[dict]
    edited_message: Optional[dict]
    channel_post: Optional[dict]
    edited_channel_post: Optional[dict]
    inline_query: Optional[dict]
    chosen_inline_result: Optional[dict]
    callback_query: Optional[dict]
    shipping_query: Optional[dict]
    pre_checkout_query: Optional[dict]
    poll: Optional[dict]
    poll_answer: Optional[dict]


app = FastAPI()
deta = Deta(os.environ['DETA_PROJECT_KEY'])
db = deta.Base('file_id')
user_db = deta.Base('quran_bot_user')
surah_db = deta.Base('surah')
reciters_db = deta.Base('reciters')

RECITATIONS = []
fetch_reciters = reciters_db.fetch()
while True:
    for i in fetch_reciters.items:
        RECITATIONS.append(i)
    if fetch_reciters.last is None:
        break
    fetch_reciters = reciters_db.fetch(last=fetch_reciters.last)

RECITATIONS.sort(key=lambda x: x['name'])

fetch_surah = surah_db.fetch()
all_surah = {}
while True:
    for i in fetch_surah.items:
        all_surah[i['key']] = i['title']
    if fetch_surah.last is None:
        break
    fetch_surah = surah_db.fetch(last=fetch_surah.last)


def download_audio(url, path):
    try:
        with httpx.stream('GET', url) as r:
            with open(path, 'wb') as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)

        return True
    except Exception as e:
        print('Downloading', e)
        return False


def start(update: Update, context: CallbackContext):
    user = update.effective_user or update.effective_chat
    name = getattr(user, "first_name", '')
    keyboard = [
        [InlineKeyboardButton("Start", callback_data='start')],
        [InlineKeyboardButton(
            "Support", url='https://www.buymeacoffee.com/chapimenge')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(WELCOME_MESSAGE.format(
        name=name), reply_markup=reply_markup)

    user_dict = user.to_dict()
    user_dict['key'] = str(user.id)
    user_db.put(user_dict)


def show_reciters(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    text = query.data
    keyboard = []
    row = []

    if text.startswith('next_reciter:'):
        intial = int(text.split(':')[1]) + 1
        end = intial + 19
        end = len(RECITATIONS) if end > len(RECITATIONS) else end
    elif text.startswith('back_reciter:'):
        intial = int(text.split(':')[1]) - 20
        end = intial + 19
        end = len(RECITATIONS) if end > len(RECITATIONS) else end
    else:
        intial = 0
        end = 20

    for reciter in RECITATIONS[intial:end]:
        row.append(InlineKeyboardButton(
            reciter['name'], callback_data=reciter['key']))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    util_btn = []
    if intial >= 0 and end < len(RECITATIONS):
        util_btn.append(InlineKeyboardButton(
            "Next", callback_data=f'next_reciter:{end}'))

    if intial != 0:
        util_btn.append(InlineKeyboardButton(
            "Back", callback_data=f'back_reciter:{intial}'))

    if util_btn:
        keyboard.append(util_btn)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Choose a reciter", reply_markup=reply_markup)


def show_suras(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    reciter_id = query.data
    keyboard = []
    row = []
    if reciter_id.startswith('next_surah:'):
        intial = int(reciter_id.split(':')[2]) + 1
        end = intial + 49
        end = 115 if end > 115 else end
        reciter_id = reciter_id.split(':')[1]
    elif reciter_id.startswith('back_surah:'):
        intial = int(reciter_id.split(':')[2]) - 50
        end = intial + 49
        end = 115 if end > 115 else end
        reciter_id = reciter_id.split(':')[1]
    else:
        intial = 1
        end = 50
    for i in range(intial, end):
        s_index = str(i).zfill(3)
        row.append(InlineKeyboardButton(
            all_surah[s_index], callback_data=f'surah:{reciter_id}:{i}'))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    util_btn = []

    if intial == 1 or intial == 51:
        util_btn.append(InlineKeyboardButton(
            "Next", callback_data=f'next_surah:{reciter_id}:{end}'))
    if intial != 1:
        util_btn.append(InlineKeyboardButton(
            "Back", callback_data=f'back_surah:{reciter_id}:{intial}'))

    keyboard.append(util_btn)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Choose a surah", reply_markup=reply_markup)


def send_audio(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    surah_id = query.data
    reciter_id = int(surah_id.split(':')[1])
    surah_id = surah_id.split(':')[2]
    surah_id = surah_id.zfill(3)
    query.edit_message_text(text='Sending audio...')
    file_id = db.get(f'{surah_id}-{reciter_id}')
    if not file_id:
        path = f'/tmp/{surah_id}-{reciter_id}.mp3'
        download_url = None
        for reciter in RECITATIONS:
            if reciter['key'] == str(reciter_id):
                download_url = reciter['download_link']
                break

        if not download_url:
            query.edit_message_text(
                text='Something went wrong, Please try again later.')
            return
        query.edit_message_text(
            text='Downloading audio, Please wait...')
        download_url = f'{download_url}/{surah_id}.mp3'
        download_audio(download_url, path)
        if not download_url or not os.path.exists(path):
            query.edit_message_text(
                text='Something went wrong, Please try again later.')

        query.edit_message_text(
            text='Uploading audio, Please wait...')
        try:
            file_id = context.bot.send_audio(chat_id=query.message.chat_id,
                                             audio=open(path, 'rb'))
            db.put({
                "key": f'{surah_id}-{reciter_id}',
                "file_id": file_id['audio']['file_id'],
                "name": all_surah[surah_id],
                "surah_number": surah_id,
                "reciter": reciter_id
            })
            query.delete_message()
            os.remove(path)
        except Exception as e:
            print(e)
            if 'File too large' in str(e):
                keyboard = [[InlineKeyboardButton(
                    'Download', url=download_url)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=FILE_TOO_LARGE, reply_markup=reply_markup)

            os.remove(path)
            raise e

    else:
        context.bot.send_audio(chat_id=query.message.chat_id,
                               audio=file_id['file_id'])

    now = datetime.now()
    today = now.strftime("%d/%m/%Y")
    stat = user_db.get(today)
    if stat:
        stat['count'] += 1
        user_db.put(stat)
    else:
        user_db.put({'key': today, 'count': 1})


def error_handler(update: Update, context: CallbackContext):
    # send message to the user
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Something went wrong, Please try again later.")


def stat(update: Update, context: CallbackContext):
    query = update.message
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_ID:
        query.reply_text(text='You are not allowed to use this command.')
        return
    query.reply_text(text='Sending total users...')
    users = user_db.fetch()
    total_users = users.count
    while users.last:
        users = user_db.fetch(last=users.last)
        total_users += users.count

    query.reply_text(text=f'Total users: {total_users}')


def register_dispatcher(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("stat", stat))

    # show reciters must filter patterns like next_reciter:20 or back_reciter:20 or start.
    dispatcher.add_handler(CallbackQueryHandler(
        show_reciters, pattern='^next_reciter:\d+$'))
    dispatcher.add_handler(CallbackQueryHandler(
        show_reciters, pattern='^back_reciter:\d+$'))
    dispatcher.add_handler(CallbackQueryHandler(
        show_reciters, pattern='^start$'))
    dispatcher.add_handler(CallbackQueryHandler(
        send_audio, pattern='^surah:\d+:\d+$'))

    dispatcher.add_handler(CallbackQueryHandler(show_suras))


def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    register_dispatcher(dispatcher)

    updater.start_polling()
    updater.idle()


@app.post("/webhook")
def webhook(data: TelegramWebhook):
    bot = Bot(token=TOKEN)
    update = Update.de_json(data.dict(), bot)
    dispatcher = Dispatcher(bot, None, workers=4, use_context=True)
    register_dispatcher(dispatcher)
    dispatcher.process_update(update)

    return {"status": "ok"}


@app.get("/")
def index():
    return {"status": "ok"}
