from telegram.ext import Updater,Dispatcher, CallbackQueryHandler, ConversationHandler,CommandHandler,Filters,MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import telegram
import json
from telegram import Bot
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
Num = 1
# conversation states
First , Second = range(2)
token=""
BOT = Bot(token)

with open('files.json') as files:
    data = json.load(files)
with open('Surah.json') as Surah:
    surah = json.load(Surah)

ONE, TWO , THREE = range(3)
def start(update, context):
    '''conversation starts here '''
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    keyboard = [
        [InlineKeyboardButton('By Surah Number', callback_data=str(ONE)),
         InlineKeyboardButton('By Surah Name',callback_data=str(TWO))],
        [ InlineKeyboardButton('All Quran', callback_data=str(THREE))]
    ]
    reply_key = InlineKeyboardMarkup(keyboard)
    welcome = """<code>As-salāmu ʿalaykum wa-raḥmatu llāhi wa-barakātuhu """ + str(user.first_name) + str(user.last_name) + """here you can get Quran Audio by surah or All at once </code>
<strong>Choose below :</strong>"""
    update.message.reply_text(
        welcome,
        reply_markup=reply_key,
        parse_mode=telegram.ParseMode.HTML
    )
    return First
def startover(update,context):
    query = update.callback_query
    user = query.message.from_user
    welcome = """<code>As-salāmu ʿalaykum wa-raḥmatu llāhi wa-barakātuhu """ + str(user.first_name) + str(user.last_name) \
    + """here you can get Quran Audio by surah or All at once </code><strong>
Choose below :</strong>"""
    keyboard = [
        [InlineKeyboardButton('By Surah Number', callback_data=str(ONE)),
         InlineKeyboardButton('By Surah Name',callback_data=str(TWO))],
        [ InlineKeyboardButton('All Quran', callback_data=str(THREE))]
    ]
    reply_key = InlineKeyboardMarkup(keyboard)
    
    # print(dir(query.message))
    logger.info("User %s started the conversation.", user.first_name)
    bot = context.bot
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=welcome,
        reply_markup=reply_key,
        parse_mode=telegram.ParseMode.HTML
    )
    return First


def bynum1(update, context):
    query = update.callback_query
    bot = context.bot
    buttons = []
    buttons_row = []
    x = 0
    for number in range(1, 58):
        buttons_row.append(InlineKeyboardButton(number, callback_data=str(number)))
        x += 1
        if x == 6:
            buttons.append(buttons_row)
            buttons_row = []
            x = 0
    if buttons_row:
        buttons.append(buttons_row)
    back_button = InlineKeyboardButton("cancel", callback_data="cancel")
    next_button = InlineKeyboardButton("next", callback_data="next")
    menu_buttons = [back_button, next_button]
    buttons.append(menu_buttons)
    query.edit_message_text("Numbers", reply_markup=InlineKeyboardMarkup(buttons) )
    return Second


def bynum2(update,context):
    query = update.callback_query
    buttons = []
    buttons_row = []
    x = 0
    for number in range(57, 115):
        buttons_row.append(InlineKeyboardButton(number, callback_data=str(number)))
        x += 1
        if x == 6:
            buttons.append(buttons_row)
            buttons_row = []
            x = 0
    if buttons_row:
        buttons.append(buttons_row)
    back_button = InlineKeyboardButton("back", callback_data="back")
    next_button = InlineKeyboardButton("cancel", callback_data="cancel")
    menu_buttons = [back_button, next_button]
    buttons.append(menu_buttons)
    query.edit_message_text("Numbers", reply_markup=InlineKeyboardMarkup(buttons))
    return Second

def byname(update,context):
    query = update.callback_query
    bot = context.bot
    keyboard = []
    num = 0
    l=[]
    r = list(surah.items()) 
    for _ in range(25):
        row =[]
        if num == 114:
            break
        for __ in range(5):
            if num == 114:
                break
            row.append(InlineKeyboardButton(r[num][1],callback_data=str(num)))
            num+=1
            print(num)
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("⬅️  BACk",callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Please Select your choice surah Name",
        reply_markup=reply_markup
    )
    return Second

def file(update,context):
    query = update.callback_query
    file_id = data[surah[str(query.data)]]
    bot = context.bot 
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="""To get started again send me /start
As-salāmu ʿalaykum wa-raḥmatu llāhi wa-barakātuhu."""
    )
    BOT.sendAudio(chat_id=query.message.chat_id , audio=file_id)
    return First
def save(update,context):
    global Num
    fil = open('a.out','a')
    print("capi", Num)
    fil.write( str(update.message.audio.file_id) + "  " + str(update.message.audio.title) + "   " + str(Num) +"\n")
    Num += 1
    fil.close()
    return First
def main():
    # Create Updater and pass the token
    updater = Updater(token,use_context=True)
    # get dispatcher to register handlers
    dp = updater.dispatcher
    #setup conversation handlerkeyboard
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)] ,
        states={ 
            First : [CallbackQueryHandler(bynum1,pattern='^' + str(ONE) + '$'),
                     CallbackQueryHandler(byname,pattern='^' + str(TWO) + '$'),
                     MessageHandler(Filters.audio, save),
                     MessageHandler(Filters.document,save)],
            Second : [CallbackQueryHandler(file,pattern=r"\d|\d\d|\d\d\d"),
                      CallbackQueryHandler(startover,pattern="back"),
                      CallbackQueryHandler(bynum2,pattern="next"),
                    ],
            THREE : []
        },
        fallbacks=[CommandHandler('start', start)] ,
        # per_message=True
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
<<<<<<< HEAD
fil.close()
=======
>>>>>>> by number done
