import sqlite3

conn = sqlite3.connect('energy_data.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS energy (
        timestamp TEXT PRIMARY KEY,
        production REAL,
        consumption REAL
    )
''')
conn.commit()
conn.close()
print("Database and table created!") 