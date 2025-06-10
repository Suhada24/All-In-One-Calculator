import sqlite3

DB_PATH = 'calculator_history.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            expression TEXT,
            result TEXT,
            type TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print('Database and table initialized successfully.')

if __name__ == '__main__':
    init_db() 