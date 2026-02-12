import sqlite3
import os
import random

def add_players(name):
    conn = sqlite3.connect('Players.db')
    cursor = conn.cursor()

    numberid = random.randint(10000000, 99999999)

    cursor.execute('''
        INSERT INTO users (name, numberid)
        values (?,?)
    ''', (name, numberid))

    conn.commit()
    conn.close()

    return numberid

def clear_all_players():
    conn = sqlite3.connect('Players.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM users')

    conn.commit()
    conn.close()

