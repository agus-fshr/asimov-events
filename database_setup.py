import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('events.db')
c = conn.cursor()

# Create the categories table
c.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')

# Create the events table
c.execute('''
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    name TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (category_id) REFERENCES categories (id)
)
''')

# Insert initial categories
categories = [("Velocistas",), ("Sumo",), ("Mini Sumo",), ("Futbol",)]
c.executemany('INSERT INTO categories (name) VALUES (?)', categories)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database setup complete and initial categories inserted.")
