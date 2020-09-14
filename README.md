    =======================
    ==== DEPENDENCIES =====
    =======================

==== Bash command for using requirements.txt

<!-- in local terminal ensure venv is activated -->
(venv) $ pip install -r requirements.txt



    =========================
    ===== LOCAL SQLITE3 =====
    =========================

==== copy [kanjidata] to EMPTY kanji_data table to match up with Heroku PostgreSQL

(1) <!-- in local terminal -->
~/<top_level_directory>$
csv-to-sqlite -f kanjidata.csv -o kanji.db -D; sqlite3 app.db 

(2) <!-- in sqlite3, update all table data -->
DELETE FROM kanji_data;
INSERT INTO kanji_data SELECT * FROM [kanjidata];
UPDATE kanji_data AS A
    SET Bushu1 = (SELECT B.Kanji FROM kanji_data B
            WHERE A.Radical1 <> '' AND B.Meaning1=A.Radical1 
            OR A.Radical1 <> '' AND B.Meaning2=A.Radical1 
            OR A.Radical1 <> '' AND B.Meaning3=A.Radical1),
        Bushu2 = (SELECT B.Kanji FROM kanji_data B
            WHERE A.Radical2 <> '' AND B.Meaning1=A.Radical2 
            OR A.Radical2 <> '' AND B.Meaning2=A.Radical2 
            OR A.Radical2 <> '' AND B.Meaning3=A.Radical2),
        Bushu3 = (SELECT B.Kanji FROM kanji_data B
            WHERE A.Radical3 <> '' AND B.Meaning1=A.Radical3 
            OR A.Radical3 <> '' AND B.Meaning2=A.Radical3 
            OR A.Radical3 <> '' AND B.Meaning3=A.Radical3),
        Bushu4 = (SELECT B.Kanji FROM kanji_data B
            WHERE A.Radical4 <> '' AND B.Meaning1=A.Radical4 
            OR A.Radical4 <> '' AND B.Meaning2=A.Radical4 
            OR A.Radical4 <> '' AND B.Meaning3=A.Radical4)
    WHERE Id > 0 AND Id < 9000;

(3) <!-- check -->
SELECT * FROM kanji_data;


==== View column names & table info
PRAGMA table_info(kanji_data);



==== Recreate kanji data table WITH Alembic
<!-- in local terminal -->
flask db upgrade


==== Recreate kanji data table WITHOUT Alembic
<!-- in sqlite3 -->
CREATE TABLE kanji_data (
    "Order" INTEGER PRIMARY KEY UNIQUE,
    Frequency VARCHAR(32) COLLATE NOCASE,
    Kanji VARCHAR(32) COLLATE NOCASE,
    Type VARCHAR(32) COLLATE NOCASE,
    Meaning1 VARCHAR(32) COLLATE NOCASE,
    Meaning2 VARCHAR(32) COLLATE NOCASE,
    Meaning3 VARCHAR(32) COLLATE NOCASE,
    Bushu1 VARCHAR(32) COLLATE NOCASE,
    Bushu2 VARCHAR(32) COLLATE NOCASE,
    Bushu3 VARCHAR(32) COLLATE NOCASE,
    Bushu4 VARCHAR(32) COLLATE NOCASE,
    Radical1 VARCHAR(32) COLLATE NOCASE,
    Radical2 VARCHAR(32) COLLATE NOCASE,
    Radical3 VARCHAR(32) COLLATE NOCASE,
    Radical4 VARCHAR(32) COLLATE NOCASE,
    Onyomi_Reading1 VARCHAR(32) COLLATE NOCASE,
    Onyomi_Reading2 VARCHAR(32) COLLATE NOCASE,
    Kunyomi_Reading1 VARCHAR(32) COLLATE NOCASE,
    Kunyomi_Reading2 VARCHAR(32) COLLATE NOCASE,
    Mnemonic VARCHAR(256),
    Notes VARCHAR(256)
);



    =============================
    ===== HEROKU POSTGRESQL =====
    =============================

==== Update postgresql kanji data table on Heroku:

(1) <!-- in local terminal -->
heroku pg:pqsl

(2) <!-- in local terminal -->
heroku run bash

(3) <!-- in Heroku terminal -->
python3 db_tools.py; exit;



==== Update postgresql schema on Heroku:

(1) <!-- in local terminal -->
heroku run bash

(2) <!-- in Heroku terminal -->
flask db migrate -m "update DB"; flask db upgrade;

<!-- if error above, update migration version manually -->

(1) <!-- in local terminal -->
heroku pg:psql;

(2) <!-- in Heroku terminal -->
SELECT * FROM alembic_version; 

(3) <!-- use above result to get revision's 'old_version_#' -->
UPDATE alembic_version SET version_num = 'new_version_#' WHERE version_num = 'old_version_#';


==== View column names & table info
\d kanji_data


==== Collation
<!-- Equivalent of Sqlite's COLLATE NOCASE -->
CREATE COLLATION case_insensitive (
    provider = icu,
    locale = 'und-u-ks-level2',
    deterministic = false
);



    ============================
    ===== LOCAL POSTGRESQL =====
    ============================

==== Login

(1) <!-- in local terminal -->
sudo -i -u postgres     # start psql
sudo -u 'linix-username' psql   # start psql directly

(2) <!-- Inside postgres -->
psql

(3) <!-- connect to kanjiremastered -->
\c kanjiremastered


==== Recreate kanji data table
<!-- Postgres doesn't take a 'COLLATE NOCASE' keyword, 
unlike sqlite3! -->

CREATE TABLE kanji_data (
    "Order" INTEGER PRIMARY KEY UNIQUE,
    Frequency VARCHAR(32),
    Kanji VARCHAR(32),
    Type VARCHAR(32),
    Meaning1 VARCHAR(32),
    Meaning2 VARCHAR(32),
    Meaning3 VARCHAR(32),
    Bushu1 VARCHAR(32),
    Bushu2 VARCHAR(32),
    Bushu3 VARCHAR(32),
    Bushu4 VARCHAR(32),
    Radical1 VARCHAR(32),
    Radical2 VARCHAR(32),
    Radical3 VARCHAR(32),
    Radical4 VARCHAR(32),
    Onyomi_Reading1 VARCHAR(32),
    Onyomi_Reading2 VARCHAR(32),
    Kunyomi_Reading1 VARCHAR(32),
    Kunyomi_Reading2 VARCHAR(32),
    Mnemonic VARCHAR(256),
    Notes VARCHAR(256)
);


==== Start/Stop postgresql

sudo /etc/init.d/postgresql restart

sudo /etc/init.d/postgresql stop



    ================
    ===== Joke =====

==== pip install no-migrane 
<!-- A database migration tool that doesn't blow -->



=====

