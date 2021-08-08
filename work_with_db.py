import sqlite3

connection = sqlite3.connect('people.db')

def row_factory_func(cursor, row):
    if(len(row) == 1):
        return row[0]
    else:
        return list(row)

connection.row_factory = row_factory_func
cursor = connection.cursor()


#print(list(cursor.execute("SELECT * FROM users")))

print(cursor.execute(f"SELECT * FROM users WHERE id == 403500796").fetchone())
