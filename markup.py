import os
import telebot
import emoji
import random
import sqlite3
from telebot import types

keys = ['id', 'name', 'sex', 'age', 'city', 'description', 'photo', 'interests', 'mode_text', 'mode_num', 'profile_created', 'username']
basic_interests = ['стройка', 'тик-ток', 'игры', 'шахматы', 'работа', 'тусовки', 'языки', 'рисование', 'бизнес', 'питомцы', 'аниме', 'программирование', 'путешествия', 'общение', 'море', 'музыка', 'фотография', 'концерты', 'торговля', 'автомобили', 'отдых', 'дизайн', 'спорт', 'литература', 'ютуб', 'маркетинг', 'экономика', 'видеоблог', 'танцы', 'стартапы', 'театр', 'дети']
editable_settings = ['Name', 'Age', 'City', 'Sex', 'Description', 'Interests', 'Photo']


# markups -- keyboards


main = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_main = types.KeyboardButton("Profile settings")
item2_main = types.KeyboardButton("Explore")
main.add(item1_main, item2_main)

back_to_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_back_to_main = types.KeyboardButton("Back to main menu")
back_to_main.add(item1_back_to_main)

back_to_settings = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_back_to_settings = types.KeyboardButton("Back to settings")
back_to_settings.add(item1_back_to_settings)

create = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_create = types.KeyboardButton("Create profile")
create.add(item1_create, item1_back_to_main)

edit = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_edit = types.KeyboardButton("Edit profile")
edit.add(item1_edit, item1_back_to_main)

sex_create = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_sex = types.KeyboardButton(emoji.emojize('Male :boy:'))
item2_sex = types.KeyboardButton(emoji.emojize('Female :girl:'))
sex_create.add(item1_sex, item2_sex, item1_back_to_main)

sex_edit = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_sex = types.KeyboardButton(emoji.emojize('Male :boy:'))
item2_sex = types.KeyboardButton(emoji.emojize('Female :girl:'))
sex_edit.add(item1_sex, item2_sex, item1_back_to_settings)

edit_profile = types.ReplyKeyboardMarkup(resize_keyboard=True)
for elem in editable_settings:
    edit_profile.add(types.KeyboardButton(elem))
edit_profile.add(item1_main)

explore_page = types.ReplyKeyboardMarkup(resize_keyboard = True)
item1_explore_page = types.KeyboardButton('Explore new')
item2_explore_page = types.KeyboardButton('Search filters')
explore_page.add(item1_explore_page, item2_explore_page, item1_back_to_main)

# special markup when user picks up interests
def create_interests(interests):
    global item1_back_to_main
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard = True)
    for elem in (set(basic_interests) - set(interests.split())):
        markup.add(types.KeyboardButton(elem))
    markup.add(types.KeyboardButton(emoji.emojize('continue:fast-forward_button:')))
    markup.add(item1_main)
    return markup
