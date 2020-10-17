from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from datetime import datetime, timedelta
import time
from app import db
from app.models import User
from app.api.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

# BASIC AUTHORIZATION
@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    interval = timedelta(minutes=30)
    if user:
        # user.reset_login_count()
        # db.session.commit()
        login_count = user.login_count
        last_login_attempt = user.last_login_attempt
        time_span = datetime.utcnow() - last_login_attempt
        print('datetime.utcnow\n', datetime.utcnow())
        print('last_login_attemp\n', last_login_attempt)
        print('time_span\n', time_span)

    if user and user.check_password(password):
        print('first condition')
        return user

    elif user and \
            login_count < 4 and \
            time_span < interval:
        print('4th condition ulic', user.login_count)
        user.set_bad_login_count()
        db.session.commit()
        print('new li cnt', user.login_count)
        return

    elif user and \
            login_count >= 4 and \
            time_span < interval:
        print('5th condition ulic', user.login_count)
        print('Wait 30 minutes')
        return user # defers return of error msg to token route

    elif user and time_span >= interval:
        print('6th condition')
        user.reset_login_count()
        db.session.commit()
        return


@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)


# TOKEN AUTHORIZATION
@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None


@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)