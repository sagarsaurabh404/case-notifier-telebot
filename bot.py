"""
CaseNotifierBot (https://t.me/CaseNotifierBot)
Get notified on cases registered at the Hon'ble Karanataka High Court, search by Case number or Advocate name
For all results, visit https://karnatakajudiciary.kar.nic.in/websitenew/causelist/causelist_Search.php
"""

import logging
import case_scraper
from dotenv import load_dotenv
import os

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler) 

# load env variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
PORT = int(os.environ.get('PORT', 5000))
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
reply_keyboard = [['Case', 'Name'],['Done']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])

def start(update, context):
    user_name = update.message.from_user.username
    first_name = update.message.from_user.first_name
    user_id = update.message.from_user.id

    logger.info(f"user_id={user_id}, user={user_name}")

    update.message.reply_text(f"Hello {first_name}. I am your CaseNotifierBot!")

    update.message.reply_text(
        "Select a category below to let me help you",
        reply_markup=markup)
    return CHOOSING


def regular_choice(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    if "case" in text.lower():
        update.message.reply_text(f"Enter a case number to search")
    elif "name" in text.lower():
        update.message.reply_text(f"Enter a name to search")

    return TYPING_REPLY


def custom_choice(update, context):
    update.message.reply_text('I did not understand what you said! Please try again')
    return TYPING_CHOICE


def received_information(update, context):
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text(f"Please wait while I search for request..",reply_markup=markup)
    
    if 'case' in category.lower():
        logger.info("User entry - case "+ str(text))
        response = case_scraper.main("case_id:"+str(text))
        if len(response) > 0:
            DATE = response['date']
            COURT_HALL = response['court_hall_num'].title()
            CAUSE_LIST = response['cause_list_num'].title()
            CASE_NUMBER = response['case_no']
            PRESIDING = response['justice'].title()
            PETITIONER = response['petitioner'].title()
            RESPONDENT =  response['respondent'].title()
            update.message.reply_text("Here's what I found!")
            update.message.reply_text(f"{DATE}\n\n{COURT_HALL} | {CAUSE_LIST}\n\nCase Number : {CASE_NUMBER}\n\n{PRESIDING}\n\nAdvocate for Pet/Appl/Comp : {PETITIONER}\n\nAdvocate for Resp : {RESPONDENT}",reply_markup=markup)
        else:
            update.message.reply_text(f"No result(s) found for {text}",reply_markup=markup)
    elif 'name' in category.lower():
        logger.info("User entry - name "+ str(text))
        responses = case_scraper.main("name:"+str(text))
        if len(responses) > 0:
            for response in responses:
                DATE = response['date']
                COURT_HALL = response['court_hall_num'].title()
                CAUSE_LIST = response['cause_list_num'].title()
                CASE_NUMBER = response['case_no']
                PRESIDING = response['justice'].title()
                PETITIONER = response['petitioner'].title()
                RESPONDENT =  response['respondent'].title()
            update.message.reply_text("Here's what I found!")
            update.message.reply_text(f"{DATE}\n\n{COURT_HALL} | {CAUSE_LIST}\n\nCase Number : {CASE_NUMBER}\n\n{PRESIDING}\n\nAdvocate for Pet/Appl/Comp : {PETITIONER}\n\nAdvocate for Resp : {RESPONDENT}",reply_markup=markup)
        else:
            update.message.reply_text(f"No result(s) found for {text}",reply_markup=markup)
    else:
        update.message.reply_text(f"I did not understand what you said! Please try again",reply_markup=markup)
    return CHOOSING


def done(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']
    update.message.reply_text("Bye!")
    update.message.reply_text("Enter /start if you want to me to start again")
    logger.info("done")
    user_data.clear()
    return ConversationHandler.END


def main():
    updater = Updater(API_KEY, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [MessageHandler(Filters.contact, start),
                       MessageHandler(Filters.regex('^(Case|Name)$'),
                                      regular_choice),
                       MessageHandler(Filters.regex('^Something else...$'),
                                      custom_choice)
                       ],

            TYPING_CHOICE: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                               regular_choice)],

            TYPING_REPLY: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                               received_information)],
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot - uncomment below line when running on local
    # updater.start_polling()

    # Start the Bot - comment below line when running on local [changes the polling method to webhook]
    updater.start_webhook(listen="0.0.0.0",port=int(PORT),url_path=API_KEY)
    updater.bot.setWebhook('https://case-notifier.herokuapp.com/' + API_KEY)


    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
       logger.error(e.message)