import sqlite3

def init_db():
    """
    Initializes the orders database.
    Creates the orders table if it doesn't exist.
    The table starts empty — orders are added as purchases are made.
    """
    # Connect to orders.db — creates the file if it doesn't exist
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()

    # Create orders table to log every successful purchase
    # timestamp is automatically set to the current time on insert
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id   INTEGER,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()