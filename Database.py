import sqlite3

conn = sqlite3.connect('product.db')
c = conn.cursor()
c.execute("""CREATE TABLE items(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_item TEXT,
                    sum TEXT)""")

conn = sqlite3.connect('product.db')
c = conn.cursor()
c.execute("""CREATE TABLE oder(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_user TEXT,
                id_item TEXT,
                sum TEXT,
                datetime DATETIME)""")
