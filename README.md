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

    
    <!-- in local terminal -->
    sudo -i -u postgres     # start psql
    sudo -u 'linix-username' psql   # start psql directly

    <!-- Inside postgres -->
    postgres=#
    \q                      # quit
    \conninfo               # check connection info


    To restart postgresql on local:
    sudo /etc/init.d/postgresql restart



===== HEROKU POSTGRESQL =====

    ==== To update postgresql kanji data table on Heroku:

    (1) <!-- in local terminal -->
    heroke pg:pqsl

    (2) <!-- Inside postgres -->
    TRUNCATE TABLE kanji_data; \q

    (3) <!-- in local terminal -->
    heroku run bash

    (4) <!-- in Heroku terminal -->
    python3 db_tools.py; exit;


    ==== To update postgresql schema on Heroku:

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



===== Joke

    ==== pip install no-migrane 
    <!-- A database migration tool that doesn't blow -->



=====

