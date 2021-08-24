import os
import telebot
import emoji
import random
import sqlite3
from telebot import types

keys = ['id', 'name', 'sex', 'age', 'city', 'description', 'photo', 'interests', 'mode_text', 'mode_num', 'profile_created', 'username']
basic_interests = ['build', 'tik-tok', 'games', 'chess', 'work', 'party', 'languages', 'art', 'business', 'pets', 'anime', 'coding', 'travel', 'chatting', 'sea', 'music', 'photo', 'concerts', 'trading', 'auto', 'vacation', 'design', 'sport', 'literature', 'youtube', 'marketing', 'economics', 'videoblog', 'dance', 'startup', 'theater', 'children']
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

explore_menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
item1_explore_menu = types.KeyboardButton('Explore new')
item2_explore_menu = types.KeyboardButton('Search filters (VIP only)')
explore_menu.add(item1_explore_menu, item2_explore_menu, item1_back_to_main)

explore_menu_vip = types.ReplyKeyboardMarkup(resize_keyboard = True)
item1_explore_menu_vip = types.KeyboardButton('Search filters')
explore_menu_vip.add(item1_explore_menu, item1_explore_menu_vip, item1_back_to_main)

explore = types.ReplyKeyboardMarkup(resize_keyboard = True)
item1_explore = types.KeyboardButton(text = emoji.emojize(':red_heart:'))
item2_explore = types.KeyboardButton(emoji.emojize(':heart_with_arrow:'))
item3_explore = types.KeyboardButton(emoji.emojize(':thumbs_down:'))
item4_explore = types.KeyboardButton(emoji.emojize(':stop_sign:'))
item1_back_to_explore_menu = types.KeyboardButton('Back to menu')
explore.row(item1_explore, item2_explore, item3_explore, item4_explore, item1_back_to_explore_menu)

explore_settings_menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
item1_explore_settings_menu = types.KeyboardButton('Age')
item2_explore_settings_menu = types.KeyboardButton('Interest')
item3_explore_settings_menu = types.KeyboardButton('City')
item4_explore_settings_menu = types.KeyboardButton('Sex')
explore_settings_menu.add(item1_explore_settings_menu)
explore_settings_menu.add(item2_explore_settings_menu)
explore_settings_menu.add(item3_explore_settings_menu)
explore_settings_menu.add(item4_explore_settings_menu)
explore_settings_menu.add(item1_back_to_explore_menu)

sex_required_edit = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1_sex = types.KeyboardButton(emoji.emojize('Male :boy:'))
item2_sex = types.KeyboardButton(emoji.emojize('Female :girl:'))
sex_required_edit.add(item1_sex, item2_sex, item1_back_to_explore_menu)

all_interests = types.ReplyKeyboardMarkup(resize_keyboard = True)
for elem in set(basic_interests):
    all_interests.add(types.KeyboardButton(elem))
all_interests.add(item1_back_to_explore_menu)

back_to_explore_menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
back_to_explore_menu.add(item1_back_to_explore_menu)

# special markup when user picks up interests
def create_interests(interests):
    global item1_back_to_main
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard = True)
    for elem in (set(basic_interests) - set(interests.split())):
        markup.add(types.KeyboardButton(elem))
    markup.add(types.KeyboardButton(emoji.emojize('continue:fast-forward_button:')))
    markup.add(item1_main)
    return markup
