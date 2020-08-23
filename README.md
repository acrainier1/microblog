Bash command for using requirements.txt:

(venv) $ pip install -r requirements.txt# microblog


===== LOCAL POSTGRESQL =====

kanjiremadmin

~$
sudo -i -u postgres     # start psql
sudo -u kanjiremadmin psql   # start psql directly

postgres=#
\q                      # quit
\conninfo               # check connection info


To restart postgresql on local:
sudo /etc/init.d/postgresql restart



===== HEROKU POSTGRESQL =====

To update postgresql on Herko:

heroku run bash;

flask db migrate -m "update DB"; flask db upgrade;

<!-- if error above, update migration version manually -->

select * from alembic_version; <!-- gets revision's old_version_# -->

update alembic_version set version_num = 'new_version_#' where version_num = 'old_version_#';

=====

