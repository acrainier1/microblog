import psycopg2
import os


# DATABASE_URL = os.environ.get('DATABASE_URL')
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()
cur.execute('SELECT * FROM user')
one = cur.fetchone()
all = cur.fetchall()


def test(msg="db tools running"):
    print(msg, "DATABASE_URL\n", DATABASE_URL)
    print(one, all)


if __name__ == '__main__':
    test()