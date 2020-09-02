import psycopg2
import os
import csv

DATABASE_URL = os.environ['DATABASE_URL']
KANJI_DATA = 'kanjidata.csv'


conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()


with open(KANJI_DATA, 'r') as f:
    next(f) # Skip the header row.
    cur.copy_expert(sql="""COPY kanji_data FROM STDIN WITH (FORMAT CSV)""", file=f)
    conn.commit()


cur.execute('SELECT * FROM kanji_data')
first_row = cur.fetchone()
cur.close()


def test(msg="db tools running"):
    print("first_row\n", first_row)


if __name__ == '__main__':
    test()