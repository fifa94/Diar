from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import json
import datetime

ALLERGIES, SYMPTOMS = range(2)
DATA_FILE = 'user_data.json'

def save_data(data):
    with open (DATA_FILE, 'a') as file:
        json.dump(data, file)
        file.write('\n')
# Commands

def load_data():
    with open(DATA_FILE, "r") as file:
        data = file.read()
    return data

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Zapinam bota')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Help zprava')


async def alergie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['Ryma', 'Kychani'], ['Zcervenani oci', 'Kozni vyrazka'], ['Otekle oci', 'jine']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text('Vyberte vaše symptomy:', reply_markup=markup)
    return ALLERGIES


async def alergie_symptoms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_symptoms = update.message.text
    user_id = update.message.from_user.id
    time = 'Time stamp'
    time_stamp = datetime.datetime.now()

    user_data = {user_id: selected_symptoms, time: time_stamp.strftime('%d-%m-%Y %H:%M:%S')}
    save_data(user_data)

    await update.message.reply_text(f"Vybrali jste: {selected_symptoms}. Děkuji!")
    return ConversationHandler.END
# Response


async def handle_response(text: str) -> str:
    processed: str = text.lower()
    return processed


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, bot_user_name: str):

    try:
        message_type: str = update.message.chat.type
        text: str = update.message.text

        print(f'User ({update.message.chat.id}) in {message_type}: {text}')

        if message_type == 'group':
            if bot_user_name in text:
                new_text: str = text.replace(bot_user_name, '').strip()
                response: str = await handle_response(new_text)
            else:
                return
        else:
            response: str = await handle_response(text)

        print('Bot response: ', response)
        await update.message.reply_text(response)
    except Exception as e:
        print('Doslo k chybe', e)

if __name__ == '__main__':
    print('reading config file')
    try:
        f = open('config.json')
        data = json.load(f)
        f.close()
    except Exception as e:
        print("Došlo k chybě při čtení konfiguračního souboru:", e)
        exit()

    print('starting bot')
    app = Application.builder().token(data['TelegramApiKey']).build()
    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('alergie', alergie)],
        states={
            ALLERGIES: [MessageHandler(filters.TEXT, alergie_symptoms)],
        },
        fallbacks=[],
    )
    app.add_handler(conv_handler)
    # Messages
    #handle_message_partial = functools.partial(handle_message, bot_user_name=data['TelegramBotName'])
    #app.add_handler(MessageHandler(filters.TEXT, handle_message_partial))
    # Errors
    # Polling
    print('polling')
    app.run_polling(poll_interval=3)
