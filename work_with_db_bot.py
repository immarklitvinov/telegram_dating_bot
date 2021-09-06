import sqlite3
import telebot
import json
from random import randint
from pprint import pprint

bot = telebot.TeleBot("1991479685:AAG2f1NodKTqFtNOBdwObC9LhchB-hNi5Js")

def row_factory_func(cursor, row):
    if(len(row) == 1):
        return row[0]
    else:
        return list(row)

users_keys = ['id', 'name', 'sex', 'age', 'city', 'description', 'photo', 'interests', 'mode_text', 'mode_num', 'profile_created', 'username', 'chat_id', 'report_status_self']

def send_profile(chat_id, user):
    caption_generated = f"{user['name']}, {user['age']}, {user['city']}\n\n{user['description']}\n\nInterests: {', '.join(user['interests'].split()) + '.'}"
    bot.send_photo(403500796, open(f"images/{'fe' * int(user['sex'] != 'M')}male/{user['id']}.jpg", 'rb'), caption = caption_generated)

def get_profile(cursor, user_id):
    global users_keys
    return dict(zip(users_keys, cursor.execute(f"SELECT * FROM users WHERE id == {user_id}").fetchone()))

@bot.message_handler(commands=['work'])
def reply(message):
    connection = sqlite3.connect('people.db')
    connection.row_factory = row_factory_func
    cursor = connection.cursor()

    db = open("people.db","rb")
    bot.send_document(message.chat.id, db)

    connection.commit()
    connection.close()

@bot.message_handler(commands=['top'])
def reply(message):
    connection = sqlite3.connect('people.db')
    connection.row_factory = row_factory_func
    cursor = connection.cursor()

    ans_arr = cursor.execute(f"SELECT id, username FROM explore_settings ORDER BY likes_got_counter DESC").fetchall()[:10]
    bot.send_message(message.chat.id, "Top-10 are:\n\n" + "\n".join(json.dumps(ans_arr)[2:-2].split("], [")))

    connection.commit()
    connection.close()

@bot.message_handler(commands=['all_id'])
def reply(message):
    connection = sqlite3.connect('people.db')
    connection.row_factory = row_factory_func
    cursor = connection.cursor()

    ans_arr = cursor.execute(f"SELECT id, username FROM users ORDER BY id").fetchall()
    bot.send_message(message.chat.id, "\n".join(json.dumps(ans_arr)[2:-2].split("], [")) + "\n\nTotal users:" + str(len(ans_arr)))

    connection.commit()
    connection.close()

@bot.message_handler(commands=['all_rate'])
def reply(message):
    connection = sqlite3.connect('people.db')
    connection.row_factory = row_factory_func
    cursor = connection.cursor()

    ans_arr = cursor.execute(f"SELECT id, username FROM explore_settings ORDER BY times_my_profile_shown DESC").fetchall()
    bot.send_message(message.chat.id, "\n".join(json.dumps(ans_arr)[2:-2].split("], [")) + "\n\nTotal users:" + str(len(ans_arr)))

    connection.commit()
    connection.close()

@bot.message_handler(content_types='text')
def reply(message):
    connection = sqlite3.connect('people.db')
    connection.row_factory = row_factory_func
    cursor = connection.cursor()

    if message.text[5:].isnumeric():
        if int(message.text[5:]) in cursor.execute(f"SELECT id FROM users").fetchall():
            user = get_profile(cursor, int(message.text[5:]))
            send_profile(403500796, user)
        else:
            bot.send_message(message.chat.id, 'Strange command')
    else:
        bot.send_message(message.chat.id, 'Whong command')

    connection.commit()
    connection.close()

bot.polling()
