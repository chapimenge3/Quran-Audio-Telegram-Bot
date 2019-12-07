from telegram.ext import Updater,Dispatcher, CallbackQueryHandler, ConversationHandler,CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import telegram
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# conversation states
First = range(1)

# callback data 
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
def bynum(update,context):
    print('here i  am ')
    query = update.callback_query
    bot = context.bot
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Third CallbackQueryHandler. Do want to start over?",
    ) 
    return First
def main():
    # Create Updater and pass the token
    updater = Updater('906470560:AAElAm238tSjLEuNzjre8uan_1I6SsFty0Y',use_context=True)
    # get dispatcher to register handlers
    dp = updater.dispatcher
    #setup conversation handlerkeyboard
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)] ,
        states={
            First : [CallbackQueryHandler(bynum,pattern='^' + str(ONE) + '$')]
        },
        fallbacks=[CommandHandler('start', start)] 
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()


