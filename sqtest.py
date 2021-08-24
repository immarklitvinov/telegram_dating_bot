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

def f(b):
    return b

print('users are:\n')
s = '''SELECT * FROM users WHERE id == {}'''
#s.format('403500796 AND age >= 10')
print(cursor.execute(s.format('403500796 AND age >= 100')).fetchall())


connection.commit()
connection.close()
