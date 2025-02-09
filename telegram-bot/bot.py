import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

import os
from dotenv import load_dotenv


# -------------------- Global variables --------------------#


load_dotenv()
TOKEN = os.getenv('TOKEN')

order = []
sub_options = []


# Set up logging
logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=logging.INFO
)


# -------------------- Commands --------------------#

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def _help(update: Update, context: ContextTypes.DEFAULT_TYPE):
	message = 'Available commands:\n\n'
	message += '/start: Start the bot\n'
	message += '/clear: Clear the order\n'
	message += '/confirm: Confirm and send the order\n'
	message += '/help: Get help\n'
	await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


# -------------------- Menu definition --------------------#

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
	message = 'Main menu\n\n'
	message += '1. Order\n'
	message += '2. Settings\n'
	message += '3. Help\n'
	await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


# -------------------- Handle menu options --------------------#


if __name__ == '__main__':
	application = ApplicationBuilder().token('8099074823:AAH4T9BmZ_ci4DmZld68QwO37ImipcGTGRE').build()

	start_handler = CommandHandler('start', start)
	unknown_handler = CommandHandler('unknown', unknown)
	help_handler = CommandHandler('help', _help)

	application.add_handler(start_handler)
	application.add_handler(help_handler)
	application.add_handler(unknown_handler)  # Should be last

	application.run_polling()
