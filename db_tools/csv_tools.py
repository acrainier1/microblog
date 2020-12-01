import sqlite3
import csv

DB_FILE = '../app.db'
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()
data = cur.execute('SELECT * FROM kanji_data')

with open('output.csv', 'wb') as f:
    writer = csv.writer(f)
    # writer.writerow(['Column 1', 'Column 2', ...])
    writer.writerows(data)