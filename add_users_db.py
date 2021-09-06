import sqlite3
from random import randint
from pprint import pprint

connection = sqlite3.connect('people.db')

def row_factory_func(cursor, row):
    if(len(row) == 1):
        return row[0]
    else:
        return list(row)

connection.row_factory = row_factory_func
cursor = connection.cursor()

# egnat 529625530, 529625530, 'egnaoo', 0, 0, 0, '', '', 'basic', 0.0, 0.0, 'clear', 0, 0, 0, 'on', ''

cursor.execute(f"INSERT INTO users VALUES (529625530, 'Ignat', 'M', '17', 'Moscow', 'Testing info description', 'images/male/529625530.jpg', ' art auto photo economy trading chess coding chatting concerts party', 'explore_menu', 0, 1, 'egnaoo', 529625530, 'not_reported')")
cursor.execute(f"INSERT INTO explore_settings VALUES (529625530, 529625530, 'egnaoo', 0, 'free', 'active', 0, 0, 'not_reported', 0, 0, 0, 0, '', '', '', -1, '[]', '[]', '[]', '[]', 0)")

#cursor.execute(f"INSERT INTO users VALUES (403500796, 'Mark', 'M', '18', 'Moscow', 'Blabla', 'images/male/403500796.jpg', ' sea chatting auto sport games vacation pets build theater trading chess children dance', 'explore_menu', 0, 1, 'marklitvinov', 403500796, 'not_reported')")
#cursor.execute(f"INSERT INTO explore_settings VALUES (403500796, 403500796, 'marklitvinov', 0, 'free', 'active', 0, 0, 'not_reported', 0, 0, 0, 0, '', '', '', -1, '[]', '[]', '[]', '[]', 0)")

cursor.execute(f"INSERT INTO users VALUES (927476617, 'Мария', 'F', '18', 'Санкт-Петербург', 'Пишу игры, работаю с друзьями в магазине одежды в качестве дизайнера и люблю всех-всех питомцев(кроме пауков)', 'images/female/927476617.jpg', ' business coding sport design dance art music', 'explore_menu', 0, 1, 'matia20', 927476617, 'not_reported')")
cursor.execute(f"INSERT INTO explore_settings VALUES (927476617, 927476617, 'matia20', 0, 'free', 'active', 0, 0, 'not_reported', 0, 0, 0, 0, '', '', '', -1, '[]', '[]', '[]', '[]', 0)")

#print()
#print(cursor.execute(f"SELECT query FROM explore_settings WHERE id == 403500796").fetchone())
#print(type(cursor.execute(f"SELECT query FROM explore_settings WHERE id == 403500796").fetchone()))
#cursor.execute("DELETE FROM users WHERE id == 403500796")
#for i in range(1, 10):
#    cursor.execute(f"INSERT INTO users VALUES ({i},'{['Mary', 'Alina'][randint(0, 1)]}','F','{randint(16, 25)}','Khabarovsk','Description','images/female/{i}.jpg',' money','main_menu',0,1,{'0123456789'[i - 1]})")

connection.commit()
connection.close()
