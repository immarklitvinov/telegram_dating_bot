import telebot
import config
from telebot import types

bot = telebot.TeleBot(config.TOKEN)
bot_me = bot.get_me()

# dict of profiles
people = {'@example_id': ['id', 'Ivan', 'Moscow', '18', 'interests', 'description', 'photo']}

markup_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_main = types.KeyboardButton("My profile")
item2_main = types.KeyboardButton("Explore new people")
markup_main.add(item1_main, item2_main)

markup_profile = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_profile = types.KeyboardButton("Create new one")
item2_profile = types.KeyboardButton("Edit already existing")
markup_profile.add(item1_profile, item2_profile)
markup_profile.add(item1_profile, item2_profile)


var_mode = ['main_menu', 0]
profile = []

'''

1 - name
2 - city
3 - age
4 - interests
5 - description
6 - photo
'''

interests = ['стройка', 'тик-ток', 'игры', 'шахматы', 'работа', 'тусовки', 'языки', 'рисование', 'бизнес', 'питомцы', 'аниме', 'программирование', 'путешествия', 'общение', 'море', 'музыка', 'фотография', 'концерты', 'торговля', 'автомобили', 'отдых', 'дизайн', 'спорт', 'литература', 'ютуб', 'маркетинг', 'экономика', 'видеоблог', 'танцы', 'стартапы', 'театр', 'дети']

markup_interests = types.ReplyKeyboardMarkup(resize_keyboard=True)
def edit_markup():
    global markup_interests




@bot.message_handler(commands=['start'])
def welcome_command(message):
    #bot.send_message(message.chat.id, 'Hello! Send /help to get full list of commands')
    bot.send_message(message.chat.id, f"Welcome, {message.from_user.first_name}!\nI am the bot, created for you to meet new people.\nSend /help to get full list of commands",
        parse_mode='html', reply_markup = markup_main)

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, '/start - Begins the dialog\n/help - Shares info about bot\n/profile - Create your profile')


@bot.message_handler(content_types=['text'])
def reply_to_message(message):
    global var_mode
    if message.chat.type == 'private':

        # creating profile
        if var_mode[0] == 'creating_profile':
            if var_mode[1] == 1:
                profile.append(message.text) # name
                var_mode[1] = 2
                bot.send_message(message.chat.id, 'What city do you live in?', reply_markup = types.ReplyKeyboardRemove()))
            elif var_mode[1] == 2:
                profile.append(message.text) # city
                var_mode[1] = 3
                bot.send_message(message.chat.id, 'How old are you?', reply_markup = types.ReplyKeyboardRemove()))
            elif var_mode[1] == 3:
                profile.append(message.text) # age
                var_mode[1] = 4
                bot.send_message(message.chat.id, 'How old are you?', reply_markup = types.ReplyKeyboardRemove()))
            elif var_mode[1] == 4:
                #interests
                var_mode[0] = 'main_menu'
                var_mode[1] = 0
                pass

        elif message.text == 'My profile':
            bot.send_message(message.chat.id, 'Choose the required option', reply_markup = markup_profile)
        elif message.text == 'Create new one':
            bot.send_message(message.chat.id, 'What is your name?', reply_markup = types.ReplyKeyboardRemove())
            var_mode[0] = 'creating_profile'
            var_mode[1] = 1
        else:
            bot.send_message(message.chat.id, 'Message recieved!')

'''
@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.send_message(message.chat.id, 'Message recieved!')

def create_profile(chat_id):

    bot.send_message(chat_id, "What city do you live in?")
    @bot.message_handler(content_types=['text'])
    def user_city(message):
        pass
'''

bot.polling()
