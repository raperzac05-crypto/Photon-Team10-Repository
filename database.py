import sqlite3
import os

def add_players(name):
    conn = sqlite3.connect('photon.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO users (name)
        values (?)
    ''', (name,))

    conn.commit()
    conn.close()

def clear_all_players():
    conn = sqlite3.connect('photon.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM users')

    conn.commit()
    conn.close()
