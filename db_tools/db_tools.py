import psycopg2
import os
import csv

DATABASE_URL = os.environ.get('DATABASE_URL')
KANJI_DATA = 'kanjidata.csv'


conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()


with open(KANJI_DATA, 'r') as f:
    next(f) # Skip the header row.
    cur.copy_expert(sql="""COPY kanji_data FROM STDIN WITH (FORMAT CSV)""", file=f)
    conn.commit()

cur.execute('''
    UPDATE kanji_data AS a

        SET a."Bushu1" = (SELECT b."Kanji" FROM kanji_data b
                WHERE a."Radical1" <> '' AND b."Meaning1"=a."Radical1" 
                   OR a."Radical1" <> '' AND b."Meaning2"=a."Radical1" 
                   OR a."Radical1" <> '' AND b."Meaning3"=a."Radical1"),

            a."Bushu2" = (SELECT b."Kanji" FROM kanji_data b
                WHERE a."Radical2" <> '' AND b."Meaning1"=a."Radical2" 
                      OR a."Radical2" <> '' AND b."Meaning2"=a."Radical2" 
                      OR a."Radical2" <> '' AND b."Meaning3"=a."Radical2"),

            a."Bushu3" = (SELECT b."Kanji" FROM kanji_data b
                WHERE a."Radical3" <> '' AND b."Meaning1"=a."Radical3" 
                    OR a."Radical3" <> '' AND b."Meaning2"=a."Radical3" 
                    OR a."Radical3" <> '' AND b."Meaning3"=a."Radical3"),

            a."Bushu4" = (SELECT b."Kanji" FROM kanji_data b
                WHERE a."Radical4" <> '' AND b."Meaning1"=a."Radical4" 
                   OR a."Radical4" <> '' AND b."Meaning2"=a."Radical4" 
                   OR a."Radical4" <> '' AND b."Meaning3"=a."Radical4")

        WHERE a."Id" > 0 AND  a."Id" < 9000 
''')
cur.execute('SELECT * FROM kanji_data')
first_row = cur.fetchone()
cur.close()


def test(msg="db tools running"):
    print("first_row\n", first_row)


if __name__ == '__main__':
    test()