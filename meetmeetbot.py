import os
import telebot
import config
import emoji
import random
import sqlite3
import markup
from markup import create_interests
from telebot import types

# creating bot
bot = telebot.TeleBot(config.TOKEN)
bot_me = bot.get_me()

# creating connection and db
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
    interests text,
    mode_text text,
    mode_num integer,
    profile_created integer,
    username text
    )""")

connection.commit()
connection.close()

# gloval variables
keys = ['id', 'name', 'sex', 'age', 'city', 'description', 'photo', 'interests', 'mode_text', 'mode_num', 'profile_created', 'username']
basic_interests = ['стройка', 'тик-ток', 'игры', 'шахматы', 'работа', 'тусовки', 'языки', 'рисование', 'бизнес', 'питомцы', 'аниме', 'программирование', 'путешествия', 'общение', 'море', 'музыка', 'фотография', 'концерты', 'торговля', 'автомобили', 'отдых', 'дизайн', 'спорт', 'литература', 'ютуб', 'маркетинг', 'экономика', 'видеоблог', 'танцы', 'стартапы', 'театр', 'дети']
editable_settings = ['Name', 'Age', 'City', 'Sex', 'Description', 'Interests', 'Photo']

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
    caption_generated = f"{user['name']}, {user['age']}, {user['city']}\n\n{user['description']}\n\nInterests: {', '.join(user['interests'].split()) + '.'}"
    bot.send_photo(chat_id, open(f"images/{'fe' * int(user['sex'] != 'M')}male/{user['id']}.jpg", 'rb'), caption = caption_generated)


# most important function to get user data from db
def get_data(cursor, user_id):
    global keys
    return dict(zip(keys, cursor.execute(f"SELECT * FROM users WHERE id == {user_id}").fetchone()))


def back_to_main_menu(cursor, user, message):
    cursor.execute(f"UPDATE users SET mode_num = 0, mode_text = 'main_menu' WHERE id = {user['id']}")
    bot.send_message(message.chat.id, 'Main menu', reply_markup = markup.main)

def back_to_edit_profile_menu(cursor, user, message):
    cursor.execute(f"UPDATE users SET mode_num = 0, mode_text = 'main_menu' WHERE id = {user['id']}")
    bot.send_message(message.chat.id, 'Edit profile menu', reply_markup = markup.edit_profile)

def create_user(cursor, message):
    cursor.execute(f"INSERT INTO users VALUES ({message.from_user.id},'','','','','','','','main_menu',0,0,{message.from_user.username})")


# handlers

@bot.message_handler(commands=['start'])
def welcome_command(message):

    connection = sqlite3.connect('people.db')
    connection.row_factory = row_factory_func
    cursor = connection.cursor()

    bot.send_message(message.chat.id, f"Welcome, {message.from_user.first_name} {message.from_user.last_name}!\nI am the bot, created for you to meet new people.\nFirst you need to create your profile in <Profile settings> button, then you will be able to explore others.\nSend /help to get full list of commands", reply_markup = markup.main)
    if(message.from_user.id not in list(cursor.execute("SELECT id FROM users"))):
        create_user(cursor, username)

    connection.commit()
    connection.close()

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.from_user.id, f"/start - Begins the dialog\n/help - Shares info about bot\n")

@bot.message_handler(content_types=['text'])
def reply_to_message(message):
    global editable_settings

    connection = sqlite3.connect('people.db')
    connection.row_factory = row_factory_func
    cursor = connection.cursor()

    user_id = message.from_user.id

    if message.chat.type == 'private':

        # creating profile
        if message.from_user.id not in list(cursor.execute("SELECT id FROM users")):
            cursor.execute(f"INSERT INTO users VALUES ({message.from_user.id},'','','','','','','','main_menu',0,0)")
            bot.send_message(message.chat.id, 'Hello! Start chatting with creating your profile in settings.', reply_markup = markup.main)

        user = get_data(cursor, user_id)

        if user['mode_text'] == 'creating_profile':
            if user['mode_num'] == 1 and message.text != 'Back to main menu':
                cursor.execute(f"UPDATE users SET name = '{message.text}', mode_num = 2 WHERE id = {user_id};") # name
                bot.send_message(message.chat.id, 'Male / Female?', reply_markup = markup.sex_create)
            elif user['mode_num'] == 2 and (message.text.find("Male") != -1 or message.text.find("Female") != -1) and message.text != 'Back to main menu':
                if(message.text.find("Male") != -1): # sex
                    cursor.execute(f"UPDATE users SET sex = 'M' WHERE id = {user_id};")
                else:
                    cursor.execute(f"UPDATE users SET sex = 'F' WHERE id = {user_id};")
                cursor.execute(f"UPDATE users SET mode_num = 3 WHERE id = {user_id};")
                bot.send_message(message.chat.id, 'What city do you live in?', reply_markup = markup.back_to_settings)
            elif user['mode_num'] == 3 and message.text != 'Back to main menu':
                cursor.execute(f"UPDATE users SET city = '{message.text}', mode_num = 4 WHERE id = {user_id};") # city
                bot.send_message(message.chat.id, 'How old are you?', reply_markup = markup.back_to_settings)
            elif user['mode_num'] == 4 and message.text != 'Back to main menu':
                cursor.execute(f"UPDATE users SET age = '{message.text}', mode_num = 5 WHERE id = {user_id};") # age
                bot.send_message(message.chat.id, emoji.emojize('Choose your interest. To end press continue:fast-forward_button: button at the bottom.'), reply_markup = create_markup.interests(user['interests']))
            elif user['mode_num'] == 5 and ('continue' not in message.text) and message.text in (set(basic_interests) - set(user['interests'].split())) and message.text != 'Back to main menu':
                cursor.execute(f"UPDATE users SET interests = '{user['interests'] + ' '  + message.text}', mode_num = 5 WHERE id = {user_id};") # append interests 1 by 1
                user = get_data(cursor, user_id)
                bot.send_message(message.chat.id, emoji.emojize('Added! Anything else? To end press continue:fast-forward_button: button at the bottom.'), reply_markup = create_markup.interests(user['interests']))
            elif user['mode_num'] == 5 and 'continue' in message.text and message.text != 'Back to main menu':
                cursor.execute(f"UPDATE users SET mode_num = 6 WHERE id = {user_id};")
                bot.send_message(message.chat.id, 'Write something about yourself here', reply_markup = markup.back_to_settings)
            elif user['mode_num'] == 6 and message.text != 'Back to main menu':
                cursor.execute(f"UPDATE users SET description = '{message.text}', mode_num = 7 WHERE id = {user_id};") # discription of profile
                bot.send_message(message.chat.id, 'Send your photo for others to see your appearence', reply_markup = markup.back_to_settings)
            else:
                cursor.execute(f"UPDATE users SET mode_num = 0, mode_text = 'main_menu' WHERE id = {user_id}")
                cursor.execute(f"UPDATE users SET name = '', sex = '', age = 0, city = '', description = '', interests = '' WHERE id = {user_id}")
                bot.send_message(message.chat.id, 'Returning you to main menu. Your profile data was cleared.', reply_markup = markup.main)

        elif message.text == 'Profile settings' or message.text == 'Back to settings':
            if(user['profile_created'] == 0):
                bot.send_message(message.chat.id, "Choose the required option", reply_markup = markup.create)
            else:
                bot.send_message(message.chat.id, "This is your profile now", reply_markup = markup.edit)
                my_profile(message.chat.id, user)

        elif message.text == 'Edit profile' and user['profile_created'] == 1:
            bot.send_message(message.chat.id, 'Choose what you want to edit.', reply_markup = markup.edit_profile)
            cursor.execute(f"UPDATE users SET mode_text = 'profile_editing', mode_num = 0 WHERE id = {user_id}")

        elif user['mode_text'] == 'profile_editing' and user['mode_num'] == 0 and message.text in editable_settings:
            if message.text == 'Interests':
                cursor.execute(f"UPDATE users SET interests = '' WHERE id = {user_id};")
                bot.send_message(message.chat.id, emoji.emojize('Choose your interest. To end press continue:fast-forward_button: button at the bottom.'), reply_markup = create_markup.interests(''))
            elif message.text == 'Sex':
                bot.send_message(message.chat.id, f"Enter the new {message.text.lower()}", reply_markup = markup.sex_edit)
            elif message.text == 'Photo':
                bot.send_message(message.chat.id, 'Send your new photo.', reply_markup = markup.back_to_settings)
            else:
                bot.send_message(message.chat.id, f"Enter the new {message.text.lower()}", reply_markup = markup.back_to_settings)
            cursor.execute(f"UPDATE users SET mode_num = {editable_settings.index(message.text) + 1} WHERE id = {user_id}")

        elif user['mode_text'] == 'profile_editing' and user['mode_num'] != 0 and message.text != 'Back to main menu':

            if user['mode_num'] == editable_settings.index('Interests') + 1:
                if ('continue' not in message.text) and message.text in (set(basic_interests) - set(user['interests'].split())):
                    cursor.execute(f"UPDATE users SET interests = '{user['interests'] + ' '  + message.text}' WHERE id = {user_id};") # append interests 1 by 1
                    user = get_data(cursor, user_id)
                    bot.send_message(message.chat.id, emoji.emojize('Added! Anything else? To end press continue:fast-forward_button: button at the bottom.'), reply_markup = create_markup.interests(user['interests']))
                elif user['mode_num'] == editable_settings.index('Interests') + 1 and 'continue' in message.text and message.text != 'Back to main menu':
                    bot.send_message(message.chat.id, 'Your interests field is updated. This is your profile now.', reply_markup = markup.edit)
                    cursor.execute(f"UPDATE users SET mode_num = 0 WHERE id = {user_id}")
                    my_profile(message.chat.id, user)

            else:
                if user['mode_num'] == editable_settings.index('Sex') + 1:
                    if 'Male' in message.text or 'Female' in message.text:
                        cursor.execute(f"UPDATE users SET sex = '{'M' if 'Male' in message.text else 'F'}', photo = 'images/{'male' if 'Male' in message.text else 'female'}/{user_id}.jpg' WHERE id = {user_id}")
                        os.rename(f"images/{'male' if user['sex'] == 'M' else 'female'}/{user_id}.jpg", f"images/{'male' if 'Male' in message.text else 'female'}/{user_id}.jpg")
                    else:
                        back_to_edit_profile_menu(cursor, user, message)
                elif user['mode_num'] == editable_settings.index('Age') + 1:
                    if message.text.isnumeric():
                        cursor.execute(f"UPDATE users SET age = {int(message.text)} WHERE id = {user_id}")
                    else:
                        back_to_edit_profile_menu(cursor, user, message)


                else:
                    cursor.execute(f"UPDATE users SET {editable_settings[user['mode_num'] - 1].lower()} = '{message.text}' WHERE id = {user_id}")
                cursor.execute(f"UPDATE users SET mode_num = 0 WHERE id = {user_id}")
                bot.send_message(message.chat.id, f"Your {editable_settings[user['mode_num'] - 1].lower()} field is updated. This is your profile now.", reply_markup = markup.edit)
                user = get_data(cursor, user_id)
                my_profile(message.chat.id, user)


        elif message.text == 'Create profile' and user['profile_created'] == 0:
            cursor.execute(f"UPDATE users SET mode_text = 'creating_profile', mode_num = 1 WHERE id = {user_id};")
            bot.send_message(message.chat.id, 'What is your name?', reply_markup = markup.back_to_settings)


        elif message.text == 'Explore' and user['mode_text'] == 'main_menu':
            bot.send_message(message.chat.id, 'Explore page', reply_markup = markup.explore_page)


        elif message.text == 'Back to main menu':
            back_to_main_menu(cursor, user, message)
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
        bot.send_message(message.chat.id, 'The creation of your profile is done. Now you can explore other profiles.', reply_markup = markup.main)

    elif user['mode_text'] == 'profile_editing' and user['mode_num'] == editable_settings.index('Photo') + 1:
        photo_download(cursor, user, message)
        cursor.execute(f"UPDATE users SET mode_num = 0, mode_text = 'profile_editing' WHERE id = {user_id}")
        bot.send_message(message.chat.id, 'Your photo is updated. This is your profile now.', reply_markup = markup.edit)
        my_profile(message.chat.id, user)

    connection.commit()
    connection.close()

bot.polling()
