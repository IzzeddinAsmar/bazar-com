import sqlite3

def init_db():
    """
    Initializes the catalog database.
    Creates the books table if it doesn't exist and pre-populates
    it with the 7 books. Uses INSERT OR IGNORE to prevent duplicates
    on service restart.
    """
    # Connect to catalog.db — creates the file if it doesn't exist
    conn = sqlite3.connect('catalog.db')
    cursor = conn.cursor()

    # Create books table with a unique constraint on title
    # to support INSERT OR IGNORE duplicate prevention
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT UNIQUE,
            topic       TEXT,
            price       REAL,
            stock_count INTEGER
        )
    """)

    # Pre-populate the catalog with 7 books across two topics.
    # INSERT OR IGNORE silently skips rows that already exist,
    # so restarting the service never creates duplicates.

    # Distributed systems books
    cursor.execute("INSERT OR IGNORE INTO books (title, topic, price, stock_count) VALUES ('How to get a good grade in DOS in 40 minutes a day', 'distributed systems', 29.99, 10)")
    cursor.execute("INSERT OR IGNORE INTO books (title, topic, price, stock_count) VALUES ('RPCs for Noobs', 'distributed systems', 24.99, 10)")
    cursor.execute("INSERT OR IGNORE INTO books (title, topic, price, stock_count) VALUES ('How to finish Project 3 on time', 'distributed systems', 14.99, 10)")

    # Undergraduate school books
    cursor.execute("INSERT OR IGNORE INTO books (title, topic, price, stock_count) VALUES ('Xen and the Art of Surviving Undergraduate School', 'undergraduate school', 19.99, 10)")
    cursor.execute("INSERT OR IGNORE INTO books (title, topic, price, stock_count) VALUES ('Cooking for the Impatient Undergrad', 'undergraduate school', 9.99, 10)")
    cursor.execute("INSERT OR IGNORE INTO books (title, topic, price, stock_count) VALUES ('Why theory classes are so hard', 'undergraduate school', 11.99, 10)")
    cursor.execute("INSERT OR IGNORE INTO books (title, topic, price, stock_count) VALUES ('Spring in the Pioneer Valley', 'undergraduate school', 9.99, 10)")

    # Commit saves all changes to disk permanently
    conn.commit()
    conn.close()