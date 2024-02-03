import sqlite3
import json

def create_table():
    # Connect to the SQLite database
    conn = sqlite3.connect('channel_music.db')
    cursor = conn.cursor()

    # Create a table with a column to store JSON documents
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS json_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data JSON
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def insert_json_data(json_data):
    # Connect to the SQLite database
    conn = sqlite3.connect('channel_music.db')
    cursor = conn.cursor()

    # Insert the JSON data into the table
    cursor.execute('INSERT INTO json_data (data) VALUES (?)', (json.dumps(json_data),))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def get_all_json_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    # Retrieve all rows from the table
    cursor.execute('SELECT data FROM json_data')
    rows = cursor.fetchall()

    # Convert the JSON data back to Python objects
    result = [json.loads(row[0]) for row in rows]

    # Close the connection
    conn.close()
    return result

