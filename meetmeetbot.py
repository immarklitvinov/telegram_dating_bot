import telebot
import config
import emoji
import random
from telebot import types

bot = telebot.TeleBot(config.TOKEN)
bot_me = bot.get_me()
var_mode = ['main_menu', 0] # selected status
profile = []
var_profile_created = False

'''

0 - id
1 - name
2 - sex
3 - city
4 - age
5 - interests
6 - description
7 - photo
'''

basic_interests = ['стройка', 'тик-ток', 'игры', 'шахматы', 'работа', 'тусовки', 'языки', 'рисование', 'бизнес', 'питомцы', 'аниме', 'программирование', 'путешествия', 'общение', 'море', 'музыка', 'фотография', 'концерты', 'торговля', 'автомобили', 'отдых', 'дизайн', 'спорт', 'литература', 'ютуб', 'маркетинг', 'экономика', 'видеоблог', 'танцы', 'стартапы', 'театр', 'дети']
random.shuffle(basic_interests)
basic_interests += ['<<continue>>']
possible_interests = basic_interests.copy()
user_interests = []

# dict of profiles    people = {'id': ['id', 'Ivan', 'M', 'Moscow', '18', 'interests_arr', 'description', 'photo']}
people = {}


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

markup_interests = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard = True)
def update_markup():
    global item1_back_to_main
    global markup_interests
    markup_interests = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard = True)
    global possible_interests
    global user_interests
    for elem in possible_interests:
        markup_interests.add(types.KeyboardButton(elem))
    markup_interests.add(item1_back_to_main)


# save photo
def photo_download(message):
    global profile
    downloaded_file = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)

    if(profile[2] == "M"):
        with open(f"images/male/{message.from_user.id}.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)
    else:
        with open(f"images/female/{message.from_user.id}.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)


# print existing profile
def my_profile(chat_id):
    global people
    p = people[chat_id]
    user_caption = f"{p[1]}, {p[4]}, {p[3]}\n\n{p[6]}\n\nInterests: {', '.join(p[5])}"
    bot.send_photo(chat_id, open(f'images/{"fe" * int(people[chat_id][2] != "M")}male/{people[chat_id][0]}.jpg', 'rb'), caption = user_caption)


# handlers

@bot.message_handler(commands=['start'])
def welcome_command(message):
    bot.send_message(message.chat.id, f"Welcome, {message.from_user.first_name}!\nI am the bot, created for you to meet new people.\nFirst you need to create your profile in <My profile> button, then you will be able to explore others.\nSend /help to get full list of commands", reply_markup = markup_main)

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.from_user.id, '/start - Begins the dialog\n/help - Shares info about bot')


@bot.message_handler(content_types=['text'])
def reply_to_message(message):
    global var_mode
    global var_profile_created
    global possible_interests
    global user_interests
    global markup_interests
    if message.chat.type == 'private':

        # creating profile
        if var_mode[0] == 'creating_profile':
            if var_mode[1] == 1:
                profile.append(message.text) # name
                var_mode[1] = 2
                bot.send_message(message.chat.id, 'Male / Female?', reply_markup = markup_sex)
            elif var_mode[1] == 2 and (message.text.find("Male") != -1 or message.text.find("Female") != -1):
                if(message.text.find("Male") != -1): # sex
                    profile.append("M")
                else:
                    profile.append("F")
                var_mode[1] = 3
                bot.send_message(message.chat.id, 'What city do you live in?', reply_markup = markup_back_to_main)
            elif var_mode[1] == 3:
                profile.append(message.text) # city
                var_mode[1] = 4
                bot.send_message(message.chat.id, 'How old are you?', reply_markup = markup_back_to_main)
            elif var_mode[1] == 4:
                profile.append(message.text) # age
                var_mode[1] = 5
                update_markup()
                bot.send_message(message.chat.id, 'What are your interests? Choose', reply_markup = markup_interests)
            elif var_mode[1] == 5 and message.text != '<<continue>>' and message.text in possible_interests:
                user_interests.append(message.text)
                possible_interests.remove(message.text)
                update_markup()
                bot.send_message(message.chat.id, 'Added! Anything else? To continue press <<continue>> button at the bottom.', reply_markup = markup_interests)
            elif var_mode[1] == 5 and message.text == '<<continue>>':
                profile.append(user_interests) # list of interests
                var_mode[1] = 6
                bot.send_message(message.chat.id, 'Write something about yourself here', reply_markup = markup_back_to_main)
            elif var_mode[1] == 6:
                profile.append(message.text) # discription of profile
                var_mode[1] = 7
                bot.send_message(message.chat.id, 'Send your photo for others to see your appearence', reply_markup = markup_back_to_main)
            elif message.text == 'Back to main menu':
                var_mode[0] = 'main_menu'
                var_mode[1] = 0
                profile.clear()
                bot.send_message(message.chat.id, 'Main menu', reply_markup = markup_main)
            else:
                var_mode[0] = 'main_menu'
                var_mode[1] = 0
                profile.clear()
                bot.send_message(message.chat.id, 'Returning you to main menu', reply_markup = markup_main)

        elif message.text == 'My profile':
            #bot.send_message(message.chat.id, f'{(!var_profile_created) * "Choose the required option" + (var_profile_created) * "Here's your profile"}', reply_markup = markup_profile)
            if(not var_profile_created):
                bot.send_message(message.chat.id, "Choose the required option", reply_markup = markup_profile)
            else:
                bot.send_message(message.chat.id, "This is your profile now", reply_markup = markup_profile)
            if(var_profile_created):
                my_profile(message.from_user.id)
        elif message.text == 'Create profile' and var_profile_created == False:
            var_mode[0] = 'creating_profile'
            var_mode[1] = 1
            profile.append(message.from_user.id)
            bot.send_message(message.chat.id, 'What is your name?', reply_markup = markup_back_to_main)
        elif message.text == 'Back to main menu':
            var_mode[0] = 'main_menu'
            var_mode[1] = 0
            profile.clear()
            bot.send_message(message.chat.id, 'Main menu', reply_markup = markup_main)
        else:
            bot.send_message(message.chat.id, 'Message recieved!')

@bot.message_handler(content_types=['photo'])
def reply_to_photo(message):
    global profile
    global people
    global var_profile_created
    if var_mode[0] == 'creating_profile' and var_mode[1] == 7:
        photo_download(message)
        var_mode[0] = 'main_menu'
        var_mode[1] = 0
        profile.append(f'/images/{"fe" * int(profile[2] != "M")}male/{message.from_user.id}.jpg')
        people[message.from_user.id] = profile.copy()
        profile.clear()
        var_profile_created = True
        markup_profile_update()
        bot.send_message(message.chat.id, 'The creation of your profile is done. Now you can explore other profiles.', reply_markup = markup_main)

bot.polling()
