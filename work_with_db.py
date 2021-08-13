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

print('users are:\n')
print(cursor.execute('SELECT * FROM users').fetchall())
print('\ntheir explore settings:\n')
print(cursor.execute('SELECT * FROM explore_settings').fetchall())




#print()
#print(cursor.execute(f"SELECT query FROM explore_settings WHERE id == 403500796").fetchone())
#print(type(cursor.execute(f"SELECT query FROM explore_settings WHERE id == 403500796").fetchone()))
#cursor.execute("DELETE FROM users WHERE id == 403500796")
#for i in range(1, 10):
#    cursor.execute(f"INSERT INTO users VALUES ({i},'{['Mary', 'Alina'][randint(0, 1)]}','F','{randint(16, 25)}','Khabarovsk','Description','images/female/{i}.jpg',' money','main_menu',0,1,{'0123456789'[i - 1]})")

connection.commit()
connection.close()
