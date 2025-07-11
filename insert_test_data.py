import sqlite3
from datetime import datetime, timedelta
import random

conn = sqlite3.connect('energy_data.db')
c = conn.cursor()
now = datetime.now().replace(minute=0, second=0, microsecond=0)
for i in range(24):
    ts = (now.replace(hour=i)).isoformat()
    prod = random.uniform(0, 2200)  # Simulate up to 2.2kW
    cons = random.uniform(500, 2500)
    c.execute('INSERT OR REPLACE INTO energy (timestamp, production, consumption) VALUES (?, ?, ?)', (ts, prod, cons))
conn.commit()
conn.close()
print("Test data inserted!") 