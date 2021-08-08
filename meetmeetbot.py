import telebot
import config
import emoji
import random
import sqlite3
from telebot import types
from teleuser import Teleuser

bot = telebot.TeleBot(config.TOKEN)
bot_me = bot.get_me()

# creating db
def row_factory_func(cursor, row):
    if(len(row) == 1):
        return row[0]
    else:
        return list(row)

connection = sqlite3.connect('people.db')
connection.row_factory = row_factory_func
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    id integer,
    name text,
    sex text,
    age text,
    city text,
    description text,
    photo text,
    interests_arr text,
    mode_text text,
    mode_num integer,
    profile_created integer
    )""")

connection.commit()
connection.close()

# gloval variables
keys = ['id', 'name', 'sex', 'age', 'city', 'description', 'photo', 'interests_arr', 'mode_text', 'mode_num', 'profile_created']
basic_interests = ['стройка', 'тик-ток', 'игры', 'шахматы', 'работа', 'тусовки', 'языки', 'рисование', 'бизнес', 'питомцы', 'аниме', 'программирование', 'путешествия', 'общение', 'море', 'музыка', 'фотография', 'концерты', 'торговля', 'автомобили', 'отдых', 'дизайн', 'спорт', 'литература', 'ютуб', 'маркетинг', 'экономика', 'видеоблог', 'танцы', 'стартапы', 'театр', 'дети']


# markups -- keyboards

markup_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_main = types.KeyboardButton("My profile")
item2_main = types.KeyboardButton("Explore")
markup_main.add(item1_main, item2_main)

markup_back_to_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_back_to_main = types.KeyboardButton("Back to main menu")
markup_back_to_main.add(item1_back_to_main)

markup_create = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_create = types.KeyboardButton("Create profile")
markup_create.add(item1_create, item1_back_to_main)

markup_edit = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_edit = types.KeyboardButton("Edit profile")
markup_edit.add(item1_edit, item1_back_to_main)

markup_sex = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_sex = types.KeyboardButton(emoji.emojize('Male :boy:'))
item2_sex = types.KeyboardButton(emoji.emojize('Female :girl:'))
markup_sex.add(item1_sex, item2_sex, item1_back_to_main)


# special markup
def create_markup_interests(interests_arr):
    global item1_back_to_main
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard = True)
    for elem in (set(basic_interests) - set(interests_arr.split())):
        markup.add(types.KeyboardButton(elem))
    markup.add(types.KeyboardButton(emoji.emojize('continue:fast-forward_button:')))
    markup.add(item1_back_to_main)
    return markup



# save photo
def photo_download(cursor, user, message):
    downloaded_file = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
    if(user['sex'] == "M"):
        with open(f"images/male/{user['id']}.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)
    else:
        with open(f"images/female/{user['id']}.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)


# print existing profile
def my_profile(chat_id, user):
    caption_generated = f"{user['name']}, {user['age']}, {user['city']}\n\n{user['description']}\n\nInterests: {', '.join(user['interests_arr'].split()) + '.'}"
    bot.send_photo(chat_id, open(f"images/{'fe' * int(user['sex'] != 'M')}male/{user['id']}.jpg", 'rb'), caption = caption_generated)


def get_data(cursor, user_id):
    global keys
    return dict(zip(keys, cursor.execute(f"SELECT * FROM users WHERE id == {user_id}").fetchone()))

# handlers

@bot.message_handler(commands=['start'])
def welcome_command(message):

    connection = sqlite3.connect('people.db')
    connection.row_factory = row_factory_func
    cursor = connection.cursor()

    bot.send_message(message.chat.id, f"Welcome, {message.from_user.first_name}!\nI am the bot, created for you to meet new people.\nFirst you need to create your profile in <My profile> button, then you will be able to explore others.\nSend /help to get full list of commands", reply_markup = markup_main)
    if(message.from_user.id not in list(cursor.execute("SELECT id FROM users"))):
        cursor.execute(f"INSERT INTO users VALUES ({message.from_user.id},'','','','','','','','main_menu',0,0)")
        #people[message.from_user.id] = Teleuser(message.from_user.id)

    connection.commit()
    connection.close()

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.from_user.id, '/start - Begins the dialog\n/help - Shares info about bot')

@bot.message_handler(content_types=['text'])
def reply_to_message(message):
    global people

    connection = sqlite3.connect('people.db')
    connection.row_factory = row_factory_func
    cursor = connection.cursor()

    user_id = message.from_user.id
    user = get_data(cursor, user_id)

    if message.chat.type == 'private':

        # creating profile
        if user['mode_text'] == 'creating_profile':
            if user['mode_num'] == 1 and message.text != 'Back to main menu':
                cursor.execute(f"UPDATE users SET name = '{message.text}', mode_num = 2 WHERE id = {user_id};") # name
                bot.send_message(message.chat.id, 'Male / Female?', reply_markup = markup_sex)
            elif user['mode_num'] == 2 and (message.text.find("Male") != -1 or message.text.find("Female") != -1) and message.text != 'Back to main menu':
                if(message.text.find("Male") != -1): # sex
                    cursor.execute(f"UPDATE users SET sex = 'M' WHERE id = {user_id};")
                else:
                    cursor.execute(f"UPDATE users SET sex = 'F' WHERE id = {user_id};")
                cursor.execute(f"UPDATE users SET mode_num = 3 WHERE id = {user_id};")
                bot.send_message(message.chat.id, 'What city do you live in?', reply_markup = markup_back_to_main)
            elif user['mode_num'] == 3 and message.text != 'Back to main menu':
                cursor.execute(f"UPDATE users SET city = '{message.text}', mode_num = 4 WHERE id = {user_id};") # city
                bot.send_message(message.chat.id, 'How old are you?', reply_markup = markup_back_to_main)
            elif user['mode_num'] == 4 and message.text != 'Back to main menu':
                cursor.execute(f"UPDATE users SET age = '{message.text}', mode_num = 5 WHERE id = {user_id};") # age
                bot.send_message(message.chat.id, emoji.emojize('Choose your interest. To end press continue:fast-forward_button: button at the bottom.'), reply_markup = create_markup_interests(user['interests_arr']))
            elif user['mode_num'] == 5 and ('continue' not in message.text) and message.text in (set(basic_interests) - set(user['interests_arr'].split())) and message.text != 'Back to main menu':
                cursor.execute(f"UPDATE users SET interests_arr = '{user['interests_arr'] + ' '  + message.text}', mode_num = 5 WHERE id = {user_id};") # append interests 1 by 1
                new_interests = user['interests_arr'] + ' '  + message.text
                bot.send_message(message.chat.id, emoji.emojize('Added! Anything else? To end press continue:fast-forward_button: button at the bottom.'), reply_markup = create_markup_interests(new_interests))
            elif user['mode_num'] == 5 and 'continue' in message.text and message.text != 'Back to main menu':
                cursor.execute(f"UPDATE users SET mode_num = 6 WHERE id = {user_id};")
                bot.send_message(message.chat.id, 'Write something about yourself here', reply_markup = markup_back_to_main)
            elif user['mode_num'] == 6 and message.text != 'Back to main menu':
                cursor.execute(f"UPDATE users SET description = '{message.text}', mode_num = 7 WHERE id = {user_id};") # discription of profile
                bot.send_message(message.chat.id, 'Send your photo for others to see your appearence', reply_markup = markup_back_to_main)
            else:
                cursor.execute(f"UPDATE users SET mode_num = 0, mode_text = 'main_menu' WHERE id = {user_id}")
                cursor.execute(f"UPDATE users SET name = '', sex = '', age = 0, city = '', description = '', interests_arr = '' WHERE id = {user_id}")
                bot.send_message(message.chat.id, 'Returning you to main menu. Your profile data was cleared.', reply_markup = markup_main)

        elif message.text == 'My profile':
            if(user['profile_created'] == 0):
                bot.send_message(message.chat.id, "Choose the required option", reply_markup = markup_create)
            else:
                bot.send_message(message.chat.id, "This is your profile now", reply_markup = markup_edit)
                my_profile(message.chat.id, user)

        elif message.text == 'Create profile' and user['profile_created'] == 0:
            cursor.execute(f"UPDATE users SET mode_text = 'creating_profile', mode_num = 1 WHERE id = {user_id};")
            bot.send_message(message.chat.id, 'What is your name?', reply_markup = markup_back_to_main)

        elif message.text == 'Back to main menu':
            cursor.execute(f"UPDATE users SET mode_num = 0, mode_text = 'main_menu' WHERE id = {user_id}")
            bot.send_message(message.chat.id, 'Main menu', reply_markup = markup_main)
        else:
            bot.send_message(message.chat.id, 'Not created yet')

    connection.commit()
    connection.close()


@bot.message_handler(content_types=['photo'])
def reply_to_photo(message):

    connection = sqlite3.connect('people.db')
    connection.row_factory = row_factory_func
    cursor = connection.cursor()

    user_id = message.from_user.id
    user = get_data(cursor, user_id)

    if user['mode_num'] == 7 and user['mode_text'] == 'creating_profile':
        photo_download(cursor, user, message)
        cursor.execute(f"UPDATE users SET mode_num = 0, mode_text = 'main_menu', photo = 'images/{'fe' * int(user['sex'] != 'M')}male/{user_id}.jpg', profile_created = 1 WHERE id = {user_id}")
        bot.send_message(message.chat.id, 'The creation of your profile is done. Now you can explore other profiles.', reply_markup = markup_main)

    connection.commit()
    connection.close()

bot.polling()
