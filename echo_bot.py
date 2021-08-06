import telebot
import config
from telebot import types

bot = telebot.TeleBot(config.TOKEN)
bot_me = bot.get_me()

# dict of profiles
people = {'@example_id': ['Moscow', 'Ivan', '18', 'Self info']}

markup_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_main = types.KeyboardButton("My profile")
item2_main = types.KeyboardButton("Explore new people")
markup_main.add(item1_main, item2_main)

markup_profile = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_profile = types.KeyboardButton("Create new one")
item2_profile = types.KeyboardButton("Edit already existing")
markup_profile.add(item1_profile, item2_profile)



@bot.message_handler(commands=['start'])
def welcome_command(message):
    #bot.send_message(message.chat.id, 'Hello! Send /help to get full list of commands')
    bot.send_message(message.chat.id, f"Welcome, {message.from_user.first_name}!\nI am the bot, created for you to meet new people.\nSend /help to get full list of commands",
        parse_mode='html', reply_markup = markup_main)

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, '/start - Begins the dialog\n/help - Shares info about bot\n/profile - Create your profile')

@bot.message_handler(commands=['My profile'])
def create_profile(message):
    bot.send_message(message.chat.id, 'Choose the required option')

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.send_message(message.chat.id, 'Message recieved!')


def create_profile(chat_id):

    bot.send_message(chat_id, "What city do you live in?")
    @bot.message_handler(content_types=['text'])
    def user_city(message):
        pass

bot.polling()
