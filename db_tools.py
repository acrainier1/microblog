import psycopg2

# DATABASE_URL=postgres://*****
DATABASE_URL = os.environ.get('DATABASE_URL')
print("DATABASE_URL=====\n", DATABASE_URL)
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

conn = psycopg2.connect("host=localhost dbname=postgres user=postgres")

def test(msg="db tools running"):
    print(msg, "DATABASE_URL\n", DATABASE_URL)


if __name__ == '__main__':
    test()