import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# Create a table for books with a genre column
cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        barcode TEXT NOT NULL UNIQUE,
        rack_no TEXT NOT NULL,
        genre TEXT NOT NULL
    )
''')

# Insert multiple book records into the table with genres
books = [
    ('Mobile Code 1', '0051111407592', '1', 'Mobile'),
    ('Mobile Code 2', '0512345000107', '1', 'Mobile'),
    ('Transformer', '9788184720099', '2', 'EEE'),
    ('Coil', '987654567786', '2', 'EEE'),
    ('DBMS', '9789333221290', '3', 'Database'),
    ('RDBMS', '9789333221287', '3', 'Database'),
    ('OS', '9789333221153', '4', 'CS'),
    ('SE', '9789333221345', '4', 'CS')
]

cursor.executemany('INSERT OR IGNORE INTO books (title, barcode, rack_no, genre) VALUES (?, ?, ?, ?)', books)

# Commit the changes and close the connection
conn.commit()
conn.close()
