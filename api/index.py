from datetime import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Dispatcher
from deta import Deta
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional


TOKEN = os.environ['TOKEN']

WELCOME_MESSAGE = """Aselamaleykum {name}

Welcome to the Quran Bot you can use this bot to listen to the recitation of the Quran with different reciters.

Please click on the button below to choose the reciter you want to listen to.
"""


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
user_db = deta.Base('user')
surah_db = deta.Base('surah')


RECITATIONS = [
    {
        "name": "Abdullah Awad al-Juhani",
        "id": 1,
        "download_link": "https://download.quranicaudio.com/quran/abdullaah_3awwaad_al-juhaynee"
    },
    {
        "name": "Abdullah Basfar",
        "id": 2,
        "download_link": "https://download.quranicaudio.com/quran/abdullaah_basfar"
    },
    {
        "name": "Abdur-Rahman as-Sudais",
        "id": 7,
        "download_link": "https://download.quranicaudio.com/quran/abdurrahmaan_as-sudays"
    },
    {
        "name": "Ali Abdur-Rahman al-Huthaify",
        "id": 8,
        "download_link": "https://download.quranicaudio.com/quran/huthayfi"
    },
    {
        "name": "AbdulMuhsin al-Qasim",
        "id": 11,
        "download_link": "https://download.quranicaudio.com/quran/abdul_muhsin_alqasim"
    },
    {
        "name": "AbdulBari ath-Thubaity",
        "id": 15,
        "download_link": "https://download.quranicaudio.com/quran/thubaity"
    },
    {
        "name": "Ahmed ibn Ali al-Ajmy",
        "id": 19,
        "download_link": "https://download.quranicaudio.com/quran/ahmed_ibn_3ali_al-3ajamy"
    },
    {
        "name": "AbdulAzeez al-Ahmad",
        "id": 21,
        "download_link": "https://download.quranicaudio.com/quran/abdulazeez_al-ahmad"
    },
    {
        "name": "AbdulBaset AbdulSamad [Murattal]",
        "id": 37,
        "download_link": "https://download.quranicaudio.com/quran/abdul_basit_murattal"
    },
    {
        "name": "AbdulWadud Haneef",
        "id": 40,
        "download_link": "https://download.quranicaudio.com/quran/abdulwadood_haneef"
    },
    {
        "name": "Aziz Alili",
        "id": 44,
        "download_link": "https://download.quranicaudio.com/quran/aziz_alili"
    },
    {
        "name": "AbdulBaset AbdulSamad [Mujawwad]",
        "id": 50,
        "download_link": "https://download.quranicaudio.com/quran/abdulbaset_mujawwad"
    },
    {
        "name": "Al-Hussayni Al-'Azazy (with Children)",
        "id": 55,
        "download_link": "https://download.quranicaudio.com/quran/alhusaynee_al3azazee_with_children"
    },
    {
        "name": "Abdur-Razaq bin Abtan al-Dulaimi [Mujawwad]",
        "id": 68,
        "download_link": "https://download.quranicaudio.com/quran/abdulrazaq_bin_abtan_al_dulaimi"
    },
    {
        "name": "Abdullah Khayat",
        "id": 72,
        "download_link": "https://download.quranicaudio.com/quran/khayat"
    },
    {
        "name": "Adel Kalbani",
        "id": 81,
        "download_link": "https://download.quranicaudio.com/quran/adel_kalbani"
    },
    {
        "name": "AbdulKareem Al Hazmi",
        "id": 106,
        "download_link": "https://download.quranicaudio.com/quran/abdulkareem_al_hazmi"
    },
    {
        "name": "Abdul-Mun'im Abdul-Mubdi'",
        "id": 108,
        "download_link": "https://download.quranicaudio.com/quran/abdulmun3im_abdulmubdi2"
    },
    {
        "name": "Abdur-Rashid Sufi",
        "id": 109,
        "download_link": "https://download.quranicaudio.com/quran/abdurrashid_sufi"
    },
    {
        "name": "Ahmad al-Huthaify",
        "id": 113,
        "download_link": "https://download.quranicaudio.com/quran/ahmad_alhuthayfi"
    },
    {
        "name": "Abu Bakr al-Shatri [Taraweeh]",
        "id": 115,
        "download_link": "https://download.quranicaudio.com/quran/abu_bakr_ash-shatri_tarawee7"
    },
    {
        "name": "Abdullah Matroud",
        "id": 124,
        "download_link": "https://download.quranicaudio.com/quran/abdullah_matroud"
    },
    {
        "name": "AbdulWadood Haneef",
        "id": 125,
        "download_link": "https://download.quranicaudio.com/quran/abdul_wadood_haneef_rare"
    },
    {
        "name": "Ahmad Nauina",
        "id": 126,
        "download_link": "https://download.quranicaudio.com/quran/ahmad_nauina"
    },
    {
        "name": "Akram Al-Alaqmi",
        "id": 127,
        "download_link": "https://download.quranicaudio.com/quran/akram_al_alaqmi"
    },
    {
        "name": "Ali Hajjaj Alsouasi",
        "id": 128,
        "download_link": "https://download.quranicaudio.com/quran/ali_hajjaj_alsouasi"
    },
    {
        "name": "Asim Abdul Aleem",
        "id": 135,
        "download_link": "https://download.quranicaudio.com/quran/asim_abdulaleem"
    },
    {
        "name": "Abdallah Abdal",
        "id": 136,
        "download_link": "https://download.quranicaudio.com/quran/abdallah_abdal"
    },
    {
        "name": "Abdullah Ali Jabir",
        "id": 158,
        "download_link": "https://download.quranicaudio.com/quran/ali_jaber"
    },
    {
        "name": "Bandar Baleela",
        "id": 160,
        "download_link": "https://download.quranicaudio.com/quran/bandar_baleelacomplete"
    },
    {
        "name": "Dr. Shawqy Hamed [Murattal]",
        "id": 74,
        "download_link": "https://download.quranicaudio.com/quran/dr.shawqy_7amedmurattal"
    },
    {
        "name": "Fares Abbad",
        "id": 14,
        "download_link": "https://download.quranicaudio.com/quran/fares"
    },
    {
        "name": "Fatih Seferagic",
        "id": 134,
        "download_link": "https://download.quranicaudio.com/quran/fatih_seferagic"
    },
    {
        "name": "Hani ar-Rifai",
        "id": 27,
        "download_link": "https://download.quranicaudio.com/quran/rifai"
    },
    {
        "name": "Hamad Sinan",
        "id": 64,
        "download_link": "https://download.quranicaudio.com/quran/hamad_sinan"
    },
    {
        "name": "Hatem Farid",
        "id": 85,
        "download_link": "https://download.quranicaudio.com/quran/hatem_faridcollection"
    },
    {
        "name": "Ibrahim Al-Jibrin",
        "id": 28,
        "download_link": "https://download.quranicaudio.com/quran/jibreen"
    },
    {
        "name": "Imad Zuhair Hafez",
        "id": 93,
        "download_link": "https://download.quranicaudio.com/quran/imad_zuhair_hafez"
    },
    {
        "name": "Ibrahim Al Akhdar",
        "id": 103,
        "download_link": "https://download.quranicaudio.com/quran/ibrahim_al_akhdar"
    },
    {
        "name": "Idrees Abkar",
        "id": 116,
        "download_link": "https://download.quranicaudio.com/quran/idrees_akbar"
    },
    {
        "name": "Khalid al-Qahtani",
        "id": 9,
        "download_link": "https://download.quranicaudio.com/quran/khaalid_al-qahtaanee"
    },
    {
        "name": "Khalid Al Ghamdi",
        "id": 105,
        "download_link": "https://download.quranicaudio.com/quran/khalid_alghamdi"
    },
    {
        "name": "Khalifah Taniji",
        "id": 161,
        "download_link": "https://download.quranicaudio.com/quran/khalifah_taniji"
    },
    {
        "name": "Mishari Rashid al-`Afasy",
        "id": 5,
        "download_link": "https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee"
    },
    {
        "name": "Muhammad Siddiq al-Minshawi",
        "id": 6,
        "download_link": "https://download.quranicaudio.com/quran/muhammad_siddeeq_al-minshaawee"
    },
    {
        "name": "Muhammad Jibreel",
        "id": 12,
        "download_link": "https://download.quranicaudio.com/quran/muhammad_jibreelcomplete"
    },
    {
        "name": "Muhammad al-Mehysni",
        "id": 26,
        "download_link": "https://download.quranicaudio.com/quran/mehysni"
    },
    {
        "name": "Muhammad al-Luhaidan",
        "id": 53,
        "download_link": "https://download.quranicaudio.com/quran/muhammad_alhaidan"
    },
    {
        "name": "Muhammad Abdul-Kareem",
        "id": 70,
        "download_link": "https://download.quranicaudio.com/quran/muhammad_abdulkareem"
    },
    {
        "name": "Mustafa al-`Azawi",
        "id": 71,
        "download_link": "https://download.quranicaudio.com/quran/mustafa_al3azzawi"
    },
    {
        "name": "Muhammad Hassan",
        "id": 79,
        "download_link": "https://download.quranicaudio.com/quran/mu7ammad_7assan"
    },
    {
        "name": "Mostafa Ismaeel",
        "id": 88,
        "download_link": "https://download.quranicaudio.com/quran/mostafa_ismaeel"
    },
    {
        "name": "Muhammad Sulaiman Patel",
        "id": 90,
        "download_link": "https://download.quranicaudio.com/quran/muhammad_patel"
    },
    {
        "name": "Mohammad Al-Tablawi",
        "id": 91,
        "download_link": "https://download.quranicaudio.com/quran/mohammad_altablawi"
    },
    {
        "name": "Mohammad Ismaeel Al-Muqaddim",
        "id": 92,
        "download_link": "https://download.quranicaudio.com/quran/mohammad_ismaeel_almuqaddim"
    },
    {
        "name": "Muhammad Ayyoob [Taraweeh]",
        "id": 107,
        "download_link": "https://download.quranicaudio.com/quran/muhammad_ayyoob_hq"
    },
    {
        "name": "Masjid Quba Taraweeh 1434",
        "id": 118,
        "download_link": "https://download.quranicaudio.com/quran/masjid_quba_1434"
    },
    {
        "name": "Muhammad Khaleel",
        "id": 119,
        "download_link": "https://download.quranicaudio.com/quran/muhammad_khaleel"
    },
    {
        "name": "Mahmoud Khaleel Al-Husary",
        "id": 122,
        "download_link": "https://download.quranicaudio.com/quran/mahmood_khaleel_al-husaree_iza3a"
    },
    {
        "name": "Mahmood Ali Al-Bana",
        "id": 129,
        "download_link": "https://download.quranicaudio.com/quran/mahmood_ali_albana"
    },
    {
        "name": "Maher al-Muaiqly",
        "id": 159,
        "download_link": "https://download.quranicaudio.com/quran/maher_almu3aiqlyyear1440"
    },
    {
        "name": "Nabil ar-Rifai",
        "id": 10,
        "download_link": "https://download.quranicaudio.com/quran/nabil_rifa3i"
    },
    {
        "name": "Nasser Al Qatami",
        "id": 104,
        "download_link": "https://download.quranicaudio.com/quran/nasser_bin_ali_alqatami"
    },
    {
        "name": "Sa`ud ash-Shuraym",
        "id": 4,
        "download_link": "https://download.quranicaudio.com/quran/sa3ood_al-shuraym"
    },
    {
        "name": "Saad al-Ghamdi",
        "id": 13,
        "download_link": "https://download.quranicaudio.com/quran/sa3d_al-ghaamidicomplete"
    },
    {
        "name": "Sahl Yasin",
        "id": 17,
        "download_link": "https://download.quranicaudio.com/quran/sahl_yaaseen"
    },
    {
        "name": "Salah Bukhatir",
        "id": 18,
        "download_link": "https://download.quranicaudio.com/quran/salaah_bukhaatir"
    },
    {
        "name": "Sudais and Shuraym",
        "id": 20,
        "download_link": "https://download.quranicaudio.com/quran/sodais_and_shuraim"
    },
    {
        "name": "Saleh al Taleb",
        "id": 35,
        "download_link": "https://download.quranicaudio.com/quran/saleh_al_taleb"
    },
    {
        "name": "Salah al-Budair",
        "id": 43,
        "download_link": "https://download.quranicaudio.com/quran/salahbudair"
    },
    {
        "name": "Sadaqat `Ali",
        "id": 61,
        "download_link": "https://download.quranicaudio.com/quran/sadaqat_ali"
    },
    {
        "name": "Salah Al-Hashim",
        "id": 80,
        "download_link": "https://download.quranicaudio.com/quran/salah_alhashim"
    },
    {
        "name": "Tawfeeq ibn Sa`id as-Sawa'igh",
        "id": 23,
        "download_link": "https://download.quranicaudio.com/quran/tawfeeq_bin_saeed-as-sawaaigh"
    },
    {
        "name": "Wadee Hammadi Al Yamani",
        "id": 130,
        "download_link": "https://download.quranicaudio.com/quran/wadee_hammadi_al-yamani"
    },
    {
        "name": "Yasser ad-Dussary",
        "id": 97,
        "download_link": "https://download.quranicaudio.com/quran/yasser_ad-dussary"
    }
]

fetch_surah = surah_db.fetch()
all_surah = {}
while True:
    for i in fetch_surah.items:
        all_surah[i['key']] = i['title']
    if fetch_surah.last is None:
        break
    fetch_surah = surah_db.fetch(last=fetch_surah.last)

def start(update: Update, context: CallbackContext):
    user = update.effective_user or update.effective_chat
    name = getattr(user, "first_name", '')
    keyboard = [
        [InlineKeyboardButton("Start", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(WELCOME_MESSAGE.format(
        name=name), reply_markup=reply_markup)

    user_dict = user.to_dict()
    user_dict['key'] = str(user.id)
    print(user_dict)
    user_db.put(user_dict)


def show_reciters(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    keyboard = []
    row = []
    for reciter in RECITATIONS:
        row.append(InlineKeyboardButton(
            reciter['name'], callback_data=reciter['id']))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
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
    query.edit_message_text(text="Choose a sura", reply_markup=reply_markup)
    


def send_audio(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    surah_id = query.data
    reciter_id = int(surah_id.split(':')[1])
    surah_id = surah_id.split(':')[2]
    surah_id = surah_id.zfill(3)
    file_id = db.get(f'{surah_id}-{reciter_id}')
    query.edit_message_text(text='Sending audio...')
    context.bot.send_audio(chat_id=query.message.chat_id,
                           audio=file_id['file_id'])
    
    now = datetime.now()
    today = now.strftime("%d/%m/%Y %H:%M:%S")
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


def register_dispatcher(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))

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
    dispatcher = Dispatcher(bot, None, workers=0, use_context=True)
    register_dispatcher(dispatcher)
    dispatcher.process_update(update)

    return {"status": "ok"}

@app.get("/")
def index():
    return {"status": "ok"}