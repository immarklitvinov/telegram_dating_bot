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

print(cursor.execute(f"SELECT id FROM users WHERE id IN ({529625530})").fetchall())

connection.commit()
connection.close()
