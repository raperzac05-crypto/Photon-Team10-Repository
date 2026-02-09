import sqlite3
import os
import random

conn = sqlite3.connect('Players.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        name TEXT NOT NULL,
        numberid INTEGER
    )
''')

for i in range(2): #Loops to add the players in the database with a random ID
    name = input("Enter name: ") #Adds a player to the database
    numberid = random.randint(10000000, 99999999) #Generates a random number to be the ID of the player

    cursor.execute('''
        INSERT INTO users (name, numberid)
        VALUES (?, ?)
    ''', (name, numberid))

conn.commit()
# conn.close()

print("Data added successfully!\n")

print("Printing data: ")

#Displays the Players in the database
cursor.execute('SELECT * FROM users')
rows = cursor.fetchall()

print(f"{'Name:':<20}{'ID:':<10}")
for row in rows:
    print(f"{row[0]:<20}{row[1]:<10}")

conn.close()