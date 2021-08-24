import os
import telebot
import config
import emoji
import random
import sqlite3
import markup
import json
from pprint import pprint
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
    username text,
    chat_id integer,
    report_status_self text
    )""")

cursor.execute("""CREATE TABLE IF NOT EXISTS explore_settings (
    id integer,
    chat_id integer,
    username text,
    likes_got_counter integer,
    account_status text,
    activity_status text,
    longtitude_self real,
    latitude_self real,
    report_status_self text,
    reported_times integer,
    times_my_profile_shown integer,

    age_min integer,
    age_max integer,
    sex_required text,
    interest_required text,
    city_required text,

    id_current integer,
    likes_to text,
    dislikes_to text,
    query text,
    seen_profiles text,
    query_length integer
    )""")

connection.commit()
connection.close()

# gloval variables
users_keys = ['id', 'name', 'sex', 'age', 'city', 'description', 'photo', 'interests', 'mode_text', 'mode_num', 'profile_created', 'username', 'chat_id', 'report_status_self']
explore_settings_keys = ['id', 'chat_id', 'username', 'likes_got_counter', 'account_status', 'activity_status', 'longtitude_self', 'latitude_self', 'report_status_self', 'reported_times', 'times_my_profile_shown', 'age_min', 'age_max', 'sex_required', 'interest_required', 'city_required', 'id_current', 'likes_to', 'dislikes_to', 'query', 'seen_profiles', 'query_length']
basic_interests = ['build', 'tik-tok', 'games', 'chess', 'work', 'party', 'languages', 'art', 'business', 'pets', 'anime', 'coding', 'travel', 'chatting', 'sea', 'music', 'photo', 'concerts', 'trading', 'auto', 'vacation', 'design', 'sport', 'literature', 'youtube', 'marketing', 'economics', 'videoblog', 'dance', 'startup', 'theater', 'children']
editable_settings = ['Name', 'Age', 'City', 'Sex', 'Description', 'Interests', 'Photo']
reactions = [emoji.emojize(':red_heart:'), emoji.emojize(':heart_with_arrow:'), emoji.emojize(':thumbs_down:'), emoji.emojize(':stop_sign:')]


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
def send_my_profile(chat_id, user):
    caption_generated = f"{user['name']}, {user['age']}, {user['city']}\n\n{user['description']}\n\nInterests: {', '.join(user['interests'].split()) + '.'}"
    bot.send_photo(chat_id, open(f"images/{'fe' * int(user['sex'] != 'M')}male/{user['id']}.jpg", 'rb'), caption = caption_generated)

def send_profile(chat_id, user):
    caption_generated = f"{user['name']}, {user['age']}, {user['city']}\n\n{user['description']}\n\nInterests: {', '.join(user['interests'].split()) + '.'}"
    bot.send_photo(chat_id, open(f"images/{'fe' * int(user['sex'] != 'M')}male/{user['id']}.jpg", 'rb'), caption = caption_generated, reply_markup = markup.explore)


# most important function to get user data from db
def get_profile(cursor, user_id):
    global users_keys
    return dict(zip(users_keys, cursor.execute(f"SELECT * FROM users WHERE id == {user_id}").fetchone()))

def get_explore_settings(cursor, user_id):
    global explore_settings_keys
    return dict(zip(explore_settings_keys, cursor.execute(f"SELECT * FROM explore_settings WHERE id == {user_id}").fetchone()))

def back_to_main_menu(cursor, user, message):
    cursor.execute(f"UPDATE users SET mode_num = 0, mode_text = 'main_menu' WHERE id = {user['id']}")
    bot.send_message(message.chat.id, 'Main menu', reply_markup = markup.main)

def back_to_edit_profile_menu(cursor, user, message):
    cursor.execute(f"UPDATE users SET mode_num = 0, mode_text = 'main_menu' WHERE id = {user['id']}")
    bot.send_message(message.chat.id, 'Edit profile menu', reply_markup = markup.edit_profile)

def create_user(cursor, message):
    cursor.execute(f"INSERT INTO users VALUES ({message.from_user.id},'','','','','','','','main_menu',0,0,'{message.from_user.username}',{message.chat.id}, 'not_reported')")
    cursor.execute(f"INSERT INTO explore_settings VALUES ({message.from_user.id}, {message.chat.id}, '{message.from_user.username}', 0, 'free', 'active', 0, 0, 'not_reported', 0, 0, 0, 0, '', '', '', -1, '[]', '[]', '[]', '[]', 0)")

def create_query(user_id, cursor, settings, user): # with filters
    if(settings['account_status'] == 'vip'):
        new_query = cursor.execute(f"SELECT id FROM users WHERE id != {user_id} AND age >= {settings['age_min']} AND age <= {settings['age_max']} AND sex == '{settings['sex_required']}' AND interests LIKE '%{settings['interest_required']}%' AND report_status_self == 'not_reported' and ").fetchall()
    else:
        new_query = cursor.execute(f"SELECT id FROM users WHERE id != {user_id}").fetchall()

    cursor.execute(f"UPDATE explore_settings SET query = '{ats(new_query)}', query_length = {len(new_query)} WHERE id = {user_id}")

def next_profile(cursor, user_id):
    anket_arr = sta(cursor.execute(f"SELECT query FROM explore_settings WHERE id == {user_id}").fetchone())
    cursor.execute(f"UPDATE explore_settings SET id_current = {anket_arr[0]}, query = '{ats(anket_arr[1:])}', query_length = {len(anket_arr) - 1} WHERE id == {user_id}")

def like(cursor, user, settings):
    bot.send_message(user['chat_id'], f"We sent {'her' if user['sex'] == 'M' else 'him'} message from you.")
    send_profile(settings['id_current'], user)
    bot.send_message(settings['id_current'], f"This user liked you! Here's the tag: @{user['username']}")
    previous = cursor.execute(f"SELECT likes_got_counter FROM explore_settings WHERE id == {settings['id_current']}").fetchone()
    cursor.execute(f"UPDATE explore_settings SET likes_got_counter = {previous + 1} WHERE id == {settings['id_current']}")

def anon_like(cursor, liker_id, liked_id):
    previous = cursor.execute(f"SELECT likes_got_counter FROM explore_settings WHERE id == {liked_id}").fetchone()
    cursor.execute(f"UPDATE explore_settings SET likes_got_counter = {previous + 1} WHERE id == {liked_id}")

    if(liker_id in sta(cursor.execute(f"SELECT likes_to FROM explore_settings WHERE id == {liked_id}").fetchone())):
        match(cursor, liker_id, liked_id)
        profile_seen(cursor, liked_id, liker_id)
    else:
        previous = sta(cursor.execute(f"SELECT likes_to FROM explore_settings WHERE id == {liker_id}").fetchone())
        cursor.execute(f"UPDATE explore_settings SET likes_to = '{[liked_id] + previous}' WHERE id == {liker_id}")

        liked_query = sta(cursor.execute(f"SELECT query FROM explore_settings WHERE id == {liked_id}").fetchone())
        cursor.execute(f"UPDATE explore_settings SET query = '{[liker_id] + liked_query}' WHERE id == {liked_id}")

        bot.send_message(liker_id, f"If this sympathy is mutual, we will let you know.")

def match(cursor, liker_id, liked_id):
    username1 = cursor.execute(f"SELECT username FROM users WHERE id == {liker_id}").fetchone()
    username2 = cursor.execute(f"SELECT username FROM users WHERE id == {liked_id}").fetchone()
    send_profile(liked_id, get_profile(cursor, liker_id))
    bot.send_message(liker_id, f"You liked each other with @{username2}. Enjoy meeting!")
    bot.send_message(liked_id, f"You liked each other with @{username1}. Enjoy meeting!")

def profile_seen(cursor, explorer_id, explored_id):
    seen = sta(cursor.execute(f"SELECT seen_profiles FROM explore_settings WHERE id == {explorer_id}").fetchone())
    cursor.execute(f"UPDATE explore_settings SET seen_profiles = '{ats([explored_id] + seen)}' WHERE id == {explorer_id}")

    times = cursor.execute(f"SELECT times_my_profile_shown FROM explore_settings WHERE id == {explored_id}").fetchone()
    cursor.execute(f"UPDATE explore_settings SET times_my_profile_shown = {times + 1} WHERE id == {explored_id}")

def dislike(cursor, explorer_id, explored_id):
    seen = sta(cursor.execute(f"SELECT seen_profiles FROM explore_settings WHERE id == {explored_id}").fetchone())
    cursor.execute(f"UPDATE explore_settings SET seen_profiles = '{ats([explorer_id] + seen)}' WHERE id == {explored_id}")
    query = sta(cursor.execute(f"SELECT query FROM explore_settings WHERE id == {explored_id}").fetchone())

    if explorer_id in query:
        cursor.execute(f"UPDATE explore_settings SET query = '{ats(query.remove(explorer_id))}', query_length = {len(query) - 1} WHERE id == {explored_id}")
    else:
        pass

def report(cursor, explorer_id, explored_id):
    reported_times_old = cursor.execute(f"SELECT reported_times FROM explore_settings WHERE id == {explored_id}").fetchone()
    times_my_profile_shown_old = cursor.execute(f"SELECT times_my_profile_shown FROM explore_settings WHERE id == {explored_id}").fetchone()
    cursor.execute(f"UPDATE explore_settings SET reported_times = {reported_times_old + 1} WHERE id == {explored_id}")

    if((reported_times_old + 1) / (times_my_profile_shown_old + 1) > 0.4 and times_my_profile_shown_old > 9):
        banned(cursor, explored_id)

    bot.send_message(explorer_id, 'You have successfully reported the user.')

def banned(cursor, explored_id):
    cursor.execute(f"UPDATE explore_settings SET report_status_self = 'reported' WHERE id == {explored_id}")
    cursor.execute(f"UPDATE users SET mode_text = 'reported' WHERE id == {explored_id}")

def vip(cursor, user_id):
    cursor.execute(f"UPDATE explore_settings SET account_status = 'vip' WHERE id == {user_id}")
    bot.send_message(user_id, f"Account changed to vip.", reply_markup = vip_markup('vip'))

def send_explore_settings(cursor, settings, user_id):
    bot.send_message(user_id, f"Your current explore settings:\n\nAge: {'none' if settings['age_min'] == 0 else str(settings['age_min']) + '-' + str(settings['age_max'])}\n\nInterest: {'none' if settings['interest_required'] == '' else settings['interest_required']}\n\nCity: {'none' if settings['city_required'] == '' else settings['city_required']}\n\nSex: {'none' if settings['sex_required'] == '' else 'Male' if settings['sex_required'] == 'M' else 'Female'}", reply_markup = /÷÷÷///markup.explore_settings_menu)

def explore_profiles(cursor, user_id):
    settings = get_explore_settings(cursor, user_id)

    if(settings['query_length'] != 0):
        next_profile(cursor, user_id)
        send_profile(user_id, get_profile(cursor, get_explore_settings(cursor, user_id)['id_current']))
    else:
        bot.send_message(user_id, 'No more users left to explore.', reply_markup = vip_markup(settings['account_status']))
        cursor.execute(f"UPDATE users SET mode_text = 'explore_menu' WHERE id = {user_id}")
        cursor.execute(f"UPDATE explore_settings SET id_current = -1 WHERE id = {user_id}")

def vip_markup(s):
    return markup.explore_menu_vip if s == 'vip' else markup.explore_menu

def fits_age(s):
    if s.count('-') == 1:
        if s[:s.index('-')].isnumeric() and s[s.index('-') + 1:].isnumeric():
            return True
    else:
        return False

def ats(arr):
    return json.dumps(arr)

def sta(string):
    return json.loads(string)

# handlers

@bot.message_handler(commands=['start'])
def welcome_command(message):

    connection = sqlite3.connect('people.db')
    connection.row_factory = row_factory_func
    cursor = connection.cursor()

    bot.send_message(message.chat.id, f"Welcome, {message.from_user.first_name} {message.from_user.last_name}!\nI am the bot, created for you to meet new people.\nFirst you need to create your profile in <Profile settings> button, then you will be able to explore others.\nSend /help to get full list of commands", reply_markup = markup.main)
    if(message.from_user.id not in list(cursor.execute("SELECT id FROM users"))):
        create_user(cursor, message)
    cursor.execute(f"UPDATE users SET mode_text = 'main_menu' WHERE id = {message.from_user.id}")

    connection.commit()
    connection.close()

@bot.message_handler(commands=['vip'])
def vip_command(message):
    connection = sqlite3.connect('people.db')
    connection.row_factory = row_factory_func
    cursor = connection.cursor()

    vip(cursor, message.from_user.id)

    connection.commit()
    connection.close()

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.from_user.id, f"/start - Begins the dialog\n/help - Shares info about bot\nLast message = {message.text}")


@bot.message_handler(content_types=['text'])
def reply_to_message(message):
    global editable_settings

    connection = sqlite3.connect('people.db')
    connection.row_factory = row_factory_func
    cursor = connection.cursor()

    user_id = message.from_user.id

    if message.chat.type == 'private' and message.from_user.id in list(cursor.execute("SELECT id FROM users")):

        user = get_profile(cursor, user_id)
        settings = get_explore_settings(cursor, user_id)

        if(settings['report_status_self'] == 'reported'):
            bot.send_message(user_id, 'You are reported so many times that we have blocked your account. Unblock via paying')
            pass


        elif message.text == 'Create profile' and user['profile_created'] == 0:
            cursor.execute(f"UPDATE users SET mode_text = 'creating_profile', mode_num = 1 WHERE id = {user_id};")
            bot.send_message(message.chat.id, 'What is your name?', reply_markup = markup.back_to_settings)

        elif message.text == 'Edit profile' and user['profile_created'] > 0:
            bot.send_message(message.chat.id, 'Choose what you want to edit.', reply_markup = markup.edit_profile)
            cursor.execute(f"UPDATE users SET mode_text = 'profile_editing', mode_num = 0 WHERE id = {user_id}")

        elif user['mode_text'] == 'creating_profile':
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
                bot.send_message(message.chat.id, emoji.emojize('Choose your interest. To end press continue:fast-forward_button: button at the bottom.'), reply_markup = create_interests(user['interests']))
            elif user['mode_num'] == 5 and ('continue' not in message.text) and message.text in (set(basic_interests) - set(user['interests'].split())) and message.text != 'Back to main menu':
                cursor.execute(f"UPDATE users SET interests = '{user['interests'] + ' '  + message.text}', mode_num = 5 WHERE id = {user_id};") # append interests 1 by 1
                user = get_profile(cursor, user_id)
                bot.send_message(message.chat.id, emoji.emojize('Added! Anything else? To end press continue:fast-forward_button: button at the bottom.'), reply_markup = create_interests(user['interests']))
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
                send_my_profile(message.chat.id, user)

        elif user['mode_text'] == 'profile_editing' and user['mode_num'] == 0 and message.text in editable_settings:
            if message.text == 'Interests':
                cursor.execute(f"UPDATE users SET interests = '' WHERE id = {user_id};")
                bot.send_message(message.chat.id, emoji.emojize('Choose your interest. To end press continue:fast-forward_button: button at the bottom.'), reply_markup = create_interests(''))
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
                    user = get_profile(cursor, user_id)
                    bot.send_message(message.chat.id, emoji.emojize('Added! Anything else? To end press continue:fast-forward_button: button at the bottom.'), reply_markup = create_interests(user['interests']))
                elif user['mode_num'] == editable_settings.index('Interests') + 1 and 'continue' in message.text and message.text != 'Back to main menu':
                    bot.send_message(message.chat.id, 'Your interests field is updated. This is your profile now.', reply_markup = markup.edit)
                    cursor.execute(f"UPDATE users SET mode_num = 0 WHERE id = {user_id}")
                    send_my_profile(message.chat.id, user)

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
                user = get_profile(cursor, user_id)
                send_my_profile(message.chat.id, user)

        elif message.text == 'Explore' and user['mode_text'] == 'main_menu' and user['profile_created'] == 1:
            if(settings['account_status'] == 'vip'):
                bot.send_message(message.chat.id, 'Explore page', reply_markup = vip_markup(settings['account_status']))
            else:
                bot.send_message(message.chat.id, 'Explore page', reply_markup = vip_markup(settings['account_status']))
            cursor.execute(f"UPDATE users SET mode_text = 'explore_menu' WHERE id = {user_id}")

        elif message.text == 'Explore' and user['mode_text'] == 'main_menu' and user['profile_created'] == 0:
            bot.send_message(user_id, f"Create profile to explore others.")

        elif message.text == 'Explore new' and user['mode_text'] == 'explore_menu' and user['profile_created'] == 1:
            create_query(message.from_user.id, cursor, settings, user)
            cursor.execute(f"UPDATE users SET mode_text = 'explore' WHERE id = {user_id}")
            bot.send_message(message.chat.id, 'New ankets for you')

            explore_profiles(cursor, user_id)

        elif user['mode_text'] == 'explore' and message.text in reactions:

            id_current = settings['id_current']

            if message.text == emoji.emojize(':red_heart:'):
                like(cursor, user, settings)
                profile_seen(cursor, id_current, user_id)
            elif message.text == emoji.emojize(':heart_with_arrow:'):
                anon_like(cursor, user_id, id_current)
            elif message.text == emoji.emojize(':thumbs_down:'):
                dislike(cursor, user_id, id_current)
            else: # report
                report(cursor, user_id, id_current)
            profile_seen(cursor, user_id, id_current)

            explore_profiles(cursor, user_id)

        elif message.text == 'Back to menu' and (user['mode_text'] == 'explore' or user['mode_text'] == 'explore_settings'):
            bot.send_message(message.chat.id, 'Explore menu', reply_markup = vip_markup(settings['account_status']))
            cursor.execute(f"UPDATE users SET mode_text = 'explore_menu' WHERE id = {user_id}")

        elif 'Search filters' in message.text and user['mode_text'] == 'explore_menu':
            if(settings['account_status'] == 'vip'):
                bot.send_message(user_id, f"Choose what to edit.", reply_markup = markup.explore_settings_menu)
                cursor.execute(f"UPDATE users SET mode_text = 'explore_settings' WHERE id == {user_id}")
                send_explore_settings(cursor, settings, user_id)
            else:
                bot.send_message(user_id, f"You are not VIP-account yet. Get it via /vip command.")

        elif user['mode_text'] == 'explore_settings' and user['mode_num'] == 0:
            if message.text == 'Interest':
                cursor.execute(f"UPDATE users SET mode_num = 1 WHERE id = {user_id};")
                bot.send_message(message.chat.id, emoji.emojize('Choose required interest.'), reply_markup = markup.all_interests)
            elif message.text == 'Age':
                cursor.execute(f"UPDATE users SET mode_num = 2 WHERE id = {user_id};")
                bot.send_message(message.chat.id, f"Enter the desired age limit separated by a hyphen without spaces like that: 16-22.", reply_markup = markup.back_to_explore_menu)
            elif message.text == 'City':
                cursor.execute(f"UPDATE users SET mode_num = 3 WHERE id = {user_id};")
                bot.send_message(message.chat.id, f"Enter the desired city", reply_markup = markup.back_to_explore_menu)
            elif message.text == 'Sex':
                cursor.execute(f"UPDATE users SET mode_num = 4 WHERE id = {user_id};")
                bot.send_message(message.chat.id, f"Enter the required sex.", reply_markup = markup.sex_required_edit)
            else:
                bot.send_message(message.chat.id, f"Now you are in explore menu.", reply_markup = vip_markup(settings['account_status']))

        elif user['mode_text'] == 'explore_settings' and user['mode_num'] != 0 and message.text != 'Back to menu':

            if user['mode_num'] == 1 and message.text in basic_interests:
                cursor.execute(f"UPDATE explore_settings SET interest_required = '{message.text}' WHERE id = {user_id};")
                bot.send_message(user_id, f"Explore settings updated.", reply_markup = markup.explore_settings_menu)
            elif user['mode_num'] == 2 and fits_age(message.text):
                age_arr = list(map(int, message.text.split('-')))
                cursor.execute(f"UPDATE explore_settings SET age_min = {age_arr[0]}, age_max = {age_arr[1]} WHERE id = {user_id};")
                bot.send_message(user_id, f"Explore settings updated.", reply_markup = markup.explore_settings_menu)
            elif user['mode_num'] == 3:
                cursor.execute(f"UPDATE explore_settings SET city_required = '{message.text}' WHERE id = {user_id};")
                bot.send_message(user_id, f"Explore settings updated.", reply_markup = markup.explore_settings_menu)
            elif user['mode_num'] == 4 and 'Male' in message.text or 'Female' in message.text:
                cursor.execute(f"UPDATE explore_settings SET sex_required = '{'M' if 'Male' in message.text else 'F'}' WHERE id = {user_id};")
                bot.send_message(user_id, f"Explore settings updated.", reply_markup = markup.explore_settings_menu)
            else:
                bot.send_message(user_id, f"Explore settings are not updated.", reply_markup = markup.explore_settings_menu)

            cursor.execute(f"UPDATE users SET mode_text = 'explore_settings', mode_num = 0 WHERE id = {user_id};")
            send_explore_settings(cursor, get_explore_settings(cursor, user_id), user_id)

        elif message.text == 'Back to main menu':
            back_to_main_menu(cursor, user, message)

        else:
            bot.send_message(message.chat.id, 'Not created yet')

    else:
        create_user(cursor, message)
        bot.send_message(message.chat.id, 'Hello! Start chatting with creating your profile in settings.', reply_markup = markup.main)


    connection.commit()
    connection.close()


@bot.message_handler(content_types=['photo'])
def reply_to_photo(message):

    connection = sqlite3.connect('people.db')
    connection.row_factory = row_factory_func
    cursor = connection.cursor()

    user_id = message.from_user.id
    user = get_profile(cursor, user_id)

    if user['mode_num'] == 7 and user['mode_text'] == 'creating_profile':
        photo_download(cursor, user, message)
        cursor.execute(f"UPDATE users SET mode_num = 0, mode_text = 'main_menu', photo = 'images/{'fe' * int(user['sex'] != 'M')}male/{user_id}.jpg', profile_created = 1 WHERE id = {user_id}")
        bot.send_message(message.chat.id, 'The creation of your profile is done. Now you can explore other profiles.', reply_markup = markup.main)

    elif user['mode_text'] == 'profile_editing' and user['mode_num'] == editable_settings.index('Photo') + 1:
        photo_download(cursor, user, message)
        cursor.execute(f"UPDATE users SET mode_num = 0, mode_text = 'profile_editing' WHERE id = {user_id}")
        bot.send_message(message.chat.id, 'Your photo is updated. This is your profile now.', reply_markup = markup.edit)
        send_my_profile(message.chat.id, user)

    connection.commit()
    connection.close()

bot.polling()
