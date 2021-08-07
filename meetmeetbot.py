import telebot
import config
import emoji
import random
from telebot import types
from teleuser import Teleuser

bot = telebot.TeleBot(config.TOKEN)
bot_me = bot.get_me()


# variables addicted to profiles
# dict of profiles    people = {'id': Teleuser}
people = {}
basic_interests = ['стройка', 'тик-ток', 'игры', 'шахматы', 'работа', 'тусовки', 'языки', 'рисование', 'бизнес', 'питомцы', 'аниме', 'программирование', 'путешествия', 'общение', 'море', 'музыка', 'фотография', 'концерты', 'торговля', 'автомобили', 'отдых', 'дизайн', 'спорт', 'литература', 'ютуб', 'маркетинг', 'экономика', 'видеоблог', 'танцы', 'стартапы', 'театр', 'дети']


# markups -- keyboards

markup_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_main = types.KeyboardButton("My profile")
item2_main = types.KeyboardButton("Explore")
markup_main.add(item1_main, item2_main)

markup_back_to_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_back_to_main = types.KeyboardButton("Back to main menu")
markup_back_to_main.add(item1_back_to_main)

markup_profile = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_profile = types.KeyboardButton("Create profile")
item2_profile = types.KeyboardButton("Edit profile")
markup_profile.add(item1_profile, item1_back_to_main)
def markup_profile_update():
    global markup_profile
    global item2_profile
    markup_profile = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_profile.add(item2_profile, item1_back_to_main)



markup_sex = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_sex = types.KeyboardButton(emoji.emojize('Male :boy:'))
item2_sex = types.KeyboardButton(emoji.emojize('Female :girl:'))
markup_sex.add(item1_sex, item2_sex, item1_back_to_main)


# special markup

item_continue = types.KeyboardButton(emoji.emojize('continue:fast-forward_button:'))
markup_interests = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard = True)
def update_markup(interests_arr):
    global item1_back_to_main
    global item_continue
    global markup_interests
    markup_interests = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard = True)
    global basic_interests
    for elem in (set(basic_interests) - set(interests_arr)):
        markup_interests.add(types.KeyboardButton(elem))
    markup_interests.add(item_continue)
    markup_interests.add(item1_back_to_main)


# save photo
def photo_download(message):
    global people
    user = people[message.from_user.id]
    downloaded_file = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)

    if(user.sex == "M"):
        with open(f"images/male/{user.id}.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)
    else:
        with open(f"images/female/{user.id}.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)


# print existing profile
def my_profile(chat_id, user_id):
    global people
    user = people[user_id]
    bot.send_photo(chat_id, open(f'images/{"fe" * int(user.sex != "M")}male/{user.id}.jpg', 'rb'), caption = str(user))


# handlers

@bot.message_handler(commands=['start'])
def welcome_command(message):
    bot.send_message(message.chat.id, f"Welcome, {message.from_user.first_name}!\nI am the bot, created for you to meet new people.\nFirst you need to create your profile in <My profile> button, then you will be able to explore others.\nSend /help to get full list of commands", reply_markup = markup_main)
    if(message.from_user.id not in people.keys()):
        people[message.from_user.id] = Teleuser(message.from_user.id)

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.from_user.id, '/start - Begins the dialog\n/help - Shares info about bot')

@bot.message_handler(content_types=['text'])
def reply_to_message(message):
    global people
    global markup_interests
    user = people[message.from_user.id]
    if message.chat.type == 'private':

        # creating profile
        if user.mode[0] == 'creating_profile':
            if user.mode[1] == 1:
                user.name = message.text # name
                user.mode[1] = 2
                bot.send_message(message.chat.id, 'Male / Female?', reply_markup = markup_sex)
            elif user.mode[1] == 2 and (message.text.find("Male") != -1 or message.text.find("Female") != -1):
                if(message.text.find("Male") != -1): # sex
                    user.sex = "M"
                else:
                    user.sex = "F"
                user.mode[1] = 3
                bot.send_message(message.chat.id, 'What city do you live in?', reply_markup = markup_back_to_main)
            elif user.mode[1] == 3:
                user.city = message.text # city
                user.mode[1] = 4
                bot.send_message(message.chat.id, 'How old are you?', reply_markup = markup_back_to_main)
            elif user.mode[1] == 4:
                user.age = message.text # age
                user.mode[1] = 5
                update_markup(user.interests_arr)
                bot.send_message(message.chat.id, emoji.emojize('Choose your interest. To end press continue:fast-forward_button: button at the bottom.'), reply_markup = markup_interests)
            elif user.mode[1] == 5 and ('continue' not in message.text) and message.text in (set(basic_interests) - set(user.interests_arr)):
                user.interests_arr.append(message.text) # append interests 1 by 1
                update_markup(user.interests_arr)
                bot.send_message(message.chat.id, emoji.emojize('Added! Anything else? To end press continue:fast-forward_button: button at the bottom.'), reply_markup = markup_interests)
            elif user.mode[1] == 5 and 'continue' in message.text:
                user.mode[1] = 6
                bot.send_message(message.chat.id, 'Write something about yourself here', reply_markup = markup_back_to_main)
            elif user.mode[1] == 6:
                user.description = message.text # discription of profile
                user.mode[1] = 7
                bot.send_message(message.chat.id, 'Send your photo for others to see your appearence', reply_markup = markup_back_to_main)
            else:
                user.mode = ['main_menu', 0]
                people[user.id] = Teleuser(user.id)
                bot.send_message(message.chat.id, 'Returning you to main menu. Your profile data was cleared.', reply_markup = markup_main)

        elif message.text == 'My profile':
            if(not user.profile_created):
                bot.send_message(message.chat.id, "Choose the required option", reply_markup = markup_profile)
            else:
                bot.send_message(message.chat.id, "This is your profile now", reply_markup = markup_profile)
                my_profile(message.chat.id, user.id)

        elif message.text == 'Create profile' and not user.profile_created:
            user.mode = ['creating_profile', 1]
            bot.send_message(message.chat.id, 'What is your name?', reply_markup = markup_back_to_main)

        elif message.text == 'Back to main menu':
            user.mode = ['main_menu', 0]
            bot.send_message(message.chat.id, 'Main menu', reply_markup = markup_main)
        else:
            bot.send_message(message.chat.id, 'Not created yet')

@bot.message_handler(content_types=['photo'])
def reply_to_photo(message):
    global people
    user = people[message.from_user.id]
    if user.mode == ['creating_profile', 7]:
        photo_download(message)
        user.mode = ['main_menu', 0]
        user.profile_created = True
        user.photo = f'/images/{"fe" * int(user.sex != "M")}male/{user.id}.jpg'
        markup_profile_update()
        bot.send_message(message.chat.id, 'The creation of your profile is done. Now you can explore other profiles.', reply_markup = markup_main)

bot.polling()
