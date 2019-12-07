from telegram.ext import Updater,Dispatcher, CallbackQueryHandler, ConversationHandler,CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import telegram
import json
from telegram import Bot
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# conversation states
First , Second = range(2)
token="906470560:AAElAm238tSjLEuNzjre8uan_1I6SsFty0Y"
BOT = Bot(token)
# callback data 

with open('files.json') as files:
    data = json.load(files)

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
    welcome = """<code>As-salāmu ʿalaykum wa-raḥmatu llāhi wa-barakātuhu """ + user.first_name + user.last_name + """here you can get Quran Audio by surah or All at once </code>
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
def bynum(update, context):
    query = update.callback_query
    bot = context.bot
    # print(dir(query.message),"\n\n\n")
    # print(bot.sendDocument)
    keyboard = []
    num = 1 
    for _ in range(12):
        row =[]
        for __ in range(10):
            if _ == 11 and num == 115:
                break
            row.append(InlineKeyboardButton(num,callback_data=str(num)))
            num+=1
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("⬅️  BACk",callback_data="BACK")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Please Select your choice surah number",
        reply_markup=reply_markup
    )
    return Second
def file(update,context):
    query = update.callback_query
    # if str(query.data).isdigit():
    #     print("yes")
    # for i in data:
    #     print(i, data[i])
    file_id = data[str(query.data)]
    bot = context.bot
    # print("the file is " , data.get(str(query.data) , "None not found"))
    # BOT.send
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=query.message.text
    )
    BOT.sendAudio(chat_id=query.message.chat_id ,
                   audio="CQADBAADKQYAAiYrWVNTaHhX3cysuRYE"
                   )
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
            First : [CallbackQueryHandler(bynum,pattern='^' + str(ONE) + '$')],
            Second : [CallbackQueryHandler(file,pattern=r"\d|\d\d|\d\d\d"),
                      CallbackQueryHandler(startover,pattern="BACK"),
                    ],


        },
        fallbacks=[CommandHandler('start', start)] ,
        # per_message=True
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()


