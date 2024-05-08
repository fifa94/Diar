from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import functools


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Bot startuje')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Help zprava')

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

        print('Bot: ', response)
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
    # Messages
    handle_message_partial = functools.partial(handle_message, botUserName=data['TelegramBotName'])
    app.add_handler(MessageHandler(filters.TEXT, handle_message_partial))
    # Errors
    # Polling
    print('polling')
    app.run_polling(poll_interval=3)
