import sqlite3

def init_db():
    conn = sqlite3.connect('catalog.db')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT UNIQUE,
            topic       TEXT,
            price       REAL,
            stock_count INTEGER
        )
    """)

    cursor.execute("INSERT OR IGNORE INTO books (title, topic, price, stock_count) VALUES ('How to get a good grade in DOS in 40 minutes a day', 'distributed systems', 29.99, 10)")
    cursor.execute("INSERT OR IGNORE INTO books (title, topic, price, stock_count) VALUES ('RPCs for Noobs', 'distributed systems', 24.99, 10)")
    cursor.execute("INSERT OR IGNORE INTO books (title, topic, price, stock_count) VALUES ('Xen and the Art of Surviving Undergraduate School', 'undergraduate school', 19.99, 10)")
    cursor.execute("INSERT OR IGNORE INTO books (title, topic, price, stock_count) VALUES ('Cooking for the Impatient Undergrad', 'undergraduate school', 9.99, 10)")

    conn.commit()
    conn.close()
