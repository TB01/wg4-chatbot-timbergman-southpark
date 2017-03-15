
# database helper is based on:
# Gareth Dwyer's tutorial on:
# Building a Chatbot using Telegram and Python
# https://www.codementor.io/garethdwyer/building-a-telegram-bot-using-python-part-1-goi5fncay
# https://github.com/sixhobbits/python-telegram-tutorial

import sqlite3

class DBHelper:

    def __init__(self, dbname="db.sqlite",journal_mode='OFF'):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.conn.execute("PRAGMA journal_mode={0}".format(journal_mode))

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS items (description text, owner text)"
        itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON items (description ASC)" 
        ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON items (owner ASC)"
        self.conn.execute(tblstmt)
        self.conn.execute(itemidx)
        self.conn.execute(ownidx)
        self.conn.commit()

    def add_item(self, item_text, owner):
        stmt = "INSERT INTO items (description, owner) VALUES (?, ?)"
        args = (item_text, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, item_text, owner):
        stmt = "DELETE FROM items WHERE description = (?) AND owner = (?)"
        args = (item_text, owner )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self, owner):
        stmt = "SELECT description FROM items WHERE owner = (?)"
        args = (owner, )
        return [x[0] for x in self.conn.execute(stmt, args)]

    def get_keys(self):
        stmt = "SELECT owner FROM items"
        return list(set([x[0] for x in self.conn.execute(stmt)]))

    
            




