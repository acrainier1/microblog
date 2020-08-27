import psycopg2
import os
import csv

DATABASE_URL = os.environ['DATABASE_URL']
KANJI_DATA = 'kanjidata.csv'


conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()



cur.execute('SELECT * FROM kanji_data')
first_row = cur.fetchall()
cur.close()


def test(msg="db tools running"):
    print("all\n", all)


if __name__ == '__main__':
    test()