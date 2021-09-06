import sqlite3
import telebot
import json
from random import randint
from pprint import pprint

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

connection = sqlite3.connect('people.db')
connection.row_factory = row_factory_func
cursor = connection.cursor()

db = open("people.db","rb")

user_arr = cursor.execute(f"SELECT * FROM users WHERE id == 403500796").fetchone()
explore_settings_arr = cursor.execute(f"SELECT * FROM explore_settings WHERE id == 403500796").fetchone()
print(user_arr)
print()
print(explore_settings_arr)

connection.commit()
connection.close()
