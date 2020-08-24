import psycopg2
import os
import csv


# DATABASE_URL = os.environ.get('DATABASE_URL')
DATABASE_URL = os.environ['DATABASE_URL']
KANJI_DATA = 'kanjidata.csv'


conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()
cur.execute('SELECT * FROM user')
one = cur.fetchone()
all = cur.fetchall()


with open(KANJI_DATA, 'r') as f:
    reader = csv.reader(f)
    next(reader) # Skip the header row.
    cur.copy_from(f, 'kanji_data', sep=',')
conn.commit()

cur.execute('SELECT * FROM kanji_data')
one_kd = cur.fetchone()
all_kd = cur.fetchall()

def test(msg="db tools running"):
    print(msg, "DATABASE_URL\n", DATABASE_URL)
    print(one, all)
    print(one_kd, all_kd)


if __name__ == '__main__':
    test()