Bash command for using requirements.txt:

(venv) $ pip install -r requirements.txt# microblog


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


==== To update postgresql on Herko:

heroku run bash;

flask db migrate -m "update DB"; flask db upgrade;

<!-- if error above, update migration version manually -->

heroku pg:psql;

SELECT * FROM alembic_version; <!-- gets revision's old_version_# -->

UPDATE alembic_version SET version_num = 'new_version_#' WHERE version_num = 'old_version_#';



=====

