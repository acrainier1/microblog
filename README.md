Bash command for using requirements.txt:

(venv) $ pip install -r requirements.txt# microblog


=====

To update postgresql on Herko:

heroku run bash

flask db migrate -m "message"

flask db upgrade


<!-- if error above, update migration version manually -->

select * from alembic_version;

update alembic_version set version_num = 'new_version_#' where version_num = 'old_version_#';



=====

