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

def get_player(player_id=None, equipment_id=None, codename=None):
    conn = sqlite3.connect('photon.db')
    cursor = conn.cursor()

    if player_id:
        cursor.execute('SELECT * FROM users WHERE playerID = ?', (player_id,))
        result = cursor.fetchone()

    elif equipment_id:
        cursor.execute('SELECT * FROM users WHERE equipmentID = ?', (equipment_id,))
        result = cursor.fetchone()

    elif codename:
        cursor.execute('SELECT * FROM users WHERE codename = ?', (codename,))
        result = cursor.fetchone()
    else:
        cursor.execute('SELECT * FROM users')
        result = cursor.fetchall()

    conn.close()
    return result
