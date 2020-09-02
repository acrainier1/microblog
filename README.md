Bash command for using requirements.txt:

(venv) $ pip install -r requirements.txt

===== LOCAL SQLITE3 =====

    ==== copy [kanjidata] to EMPTY kanji_data table to match up with Heroku PGSQL

    (1) DELETE FROM * kanji_data;

    (2) INSERT INTO kanji_data SELECT * FROM [kanjidata];

    ==== view column names

    PRAGMA table_info(kanji_data);



===== LOCAL POSTGRESQL =====

    ==== Login

    kanjiremastered

    ~$
    sudo -i -u postgres     # start psql
    sudo -u kanjiremastered psql   # start psql directly

    postgres=#
    \q                      # quit
    \conninfo               # check connection info


    To restart postgresql on local:
    sudo /etc/init.d/postgresql restart



===== HEROKU POSTGRESQL =====

    ==== To update postgresql kanji data table on Herko:
    <!-- in local terminal -->
    (1) heroke pg:pqsl

    <!-- Inside postgres -->
    (2) TRUNCATE TABLE kanji_data; \q

    <!-- in local terminal -->
    (3) heroku run bash;

    <!-- in Heroku terminal -->
    (4) python3 db_tools.py; exit;


    ==== To update postgresql schema on Herko:

    heroku run bash

    flask db migrate -m "update DB"; flask db upgrade;

    <!-- if error above, update migration version manually -->

    heroku pg:psql;

    SELECT * FROM alembic_version; <!-- gets revision's old_version_# -->

    UPDATE alembic_version SET version_num = 'new_version_#' WHERE version_num = 'old_version_#';



===== Joke

    ==== pip install no-migrane 
    <!-- A database migration tool that doesn't blow -->



=====

