import psycopg2
import os


# DATABASE_URL = os.environ.get('DATABASE_URL')
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


def test(msg="db tools running"):
    print(msg, "DATABASE_URL\n", DATABASE_URL)


if __name__ == '__main__':
    test()