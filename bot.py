#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple Bot to store intros for users.
"""

import logging
from read_config import config_parser
import hashlib
from tinydb import TinyDB, Query
from telegram.ext import Updater, CommandHandler
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize DB and tables
db = TinyDB('./db.json')
users_table = db.table('users')
permission_table = db.table('permissions')
# Create quary object for DB
quary = Query()

# Read config
config = config_parser()

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Ahoy and welcome abord,\nif you want me to '
                              'remembr you please write\n/remember followed by '
                              'your intro if you want to see someone elses '
                              'intro please enter\n/whois followed by their '
                              'username')


def helper(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help?! THERE IS NO HELP FOR YOU!")


def remember(update, context):
    """Saves user intro"""
    # Verify user permissions
    username = update.message.chat.username
    if verify_user(username):
        # Clear the string from command
        intro = str(update.message.text).replace('/remember ', '')
        # Insert or update user in DB
        users_table.upsert({'user': username.upper(), 'intro': intro},
                        quary.user == username.upper())
        update.message.reply_text('I now remember you :)')
    # If user is not known ask them to identify themselves
    else:
        update.message.reply_text("Identify yourself! (use /identify)")


def who_is(update, context):
    """Show who is someone by the name given"""
    # Verify user permissions
    username = update.message.chat.username
    if verify_user(username):
        # Clear the string from command
        name = str(update.message.text).replace('/whois ', '')
        try:
            # Quary db for user intro
            intro = users_table.search(quary.user == name.upper())[0]["intro"]
        except:
            update.message.reply_text(f'I dont think I know someone named {name} arggg!')
            return
        update.message.reply_text(intro)
    # If user is not known ask them to identify themselves
    else:
        update.message.reply_text("Identify yourself! (use /identify)")


def identify(update, context):
    """Allows user to identify using password"""
    username = update.message.chat.username
    password = hashlib.sha512(update.message.text.replace('/identify ', '')
                                .encode("utf-8")).hexdigest()
    if "PASSWORD_HASH" in os.environ:
        password_hash = os.environ["PASSWORD_HASH"]
    else:
        password_hash = config["password"]

    if password == password_hash:
        permission_table.upsert({'user': username.upper()},
                                quary.user == username.upper(),)
        update.message.reply_text("you know what you are talking about!")
    else:
        update.message.reply_text("that is not the password!! "
                                  "tell me what is the secret password or"
                                  " I'll throw you to the sharks")


def verify_user(user_name):
    """Verifys user is in permissions db"""
    user_search = permission_table.search(quary.user == user_name.upper())
    if user_search:
        return True
    else:
        return False


def list_all(update, context):
    """lists all known intros"""
    # Verify user permissions
    username = update.message.chat.username
    if verify_user(username):
        # Quary db for user intro
        all_users = users_table.all()
        message = ''
        for user in all_users:
            message += f"user: {user['user']}\n{user['intro']}\n\n"
        update.message.reply_text(message)
    # If user is not known ask them to identify themselves
    else:
        update.message.reply_text("Identify yourself! (use /identify)")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    update.message.reply_text("I don't feel very well :(")


def main():
    """Start the bot."""
    if "BOT_TOKEN" in os.environ:
        token = os.environ["BOT_TOKEN"]
    else:
        token = config["token"]
    # Create the Updater object and pass it bot's token.
    updater = Updater(token,
                      use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Set commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helper))
    dp.add_handler(CommandHandler("remember", remember))
    dp.add_handler(CommandHandler("whois", who_is))
    dp.add_handler(CommandHandler("identify", identify))
    dp.add_handler(CommandHandler("all_intros", list_all))

    # Set error handler to log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT.
    updater.idle()



if __name__ == '__main__':
    main()
