import psycopg2
import os
import csv

DATABASE_URL = os.environ.get('DATABASE_URL')
KANJI_DATA = 'kanjidatA.csv'


conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()


with open(KANJI_DATA, 'r') as f:
    next(f) # Skip the header row.
    cur.copy_expert(sql="""COPY kanji_data FROM STDIN WITH (FORMAT CSV)""", file=f)
    conn.commit()

cur.execute('''
    UPDATE kanji_data AS A

        SET "Bushu1" = (SELECT B."Kanji" FROM kanji_data B
                WHERE A."Radical1" <> '' AND B."Meaning1"=A."Radical1" 
                   OR A."Radical1" <> '' AND B."Meaning2"=A."Radical1" 
                   OR A."Radical1" <> '' AND B."Meaning3"=A."Radical1"),

            "Bushu2" = (SELECT B."Kanji" FROM kanji_data B
                WHERE A."Radical2" <> '' AND B."Meaning1"=A."Radical2" 
                   OR A."Radical2" <> '' AND B."Meaning2"=A."Radical2" 
                   OR A."Radical2" <> '' AND B."Meaning3"=A."Radical2"),

            "Bushu3" = (SELECT B."Kanji" FROM kanji_data B
                WHERE A."Radical3" <> '' AND B."Meaning1"=A."Radical3" 
                   OR A."Radical3" <> '' AND B."Meaning2"=A."Radical3" 
                   OR A."Radical3" <> '' AND B."Meaning3"=A."Radical3"),

            "Bushu4" = (SELECT B."Kanji" FROM kanji_data B
                WHERE A."Radical4" <> '' AND B."Meaning1"=A."Radical4" 
                   OR A."Radical4" <> '' AND B."Meaning2"=A."Radical4" 
                   OR A."Radical4" <> '' AND B."Meaning3"=A."Radical4")

        WHERE A."Id" > 0 AND  A."Id" < 9000
''')
cur.execute('SELECT * FROM kanji_data')
first_row = cur.fetchone()
cur.close()


def test(msg="db tools running"):
    print("first_row\n", first_row)


if __name__ == '__main__':
    test()