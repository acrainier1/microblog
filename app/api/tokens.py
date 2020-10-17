from flask import jsonify, request
from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth


# Generate user tokens
@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    
    login_count = basic_auth.current_user().check_login_count()
    last_login_attempt = basic_auth.current_user().last_login_attempt
    time_span = datetime.utcnow() - last_login_attempt
    interval = timedelta(minutes=30)

    if login_count < 4:
        print('first condition')
        user.reset_login_count()
        token = basic_auth.current_user().get_token()
        db.session.commit()
        return jsonify({'token': token})
    
    elif login_count >= 4 and time_span >= interval:
        print('second condition')
        user.reset_login_count()
        token = basic_auth.current_user().get_token()
        db.session.commit()
        return jsonify({'token': token})

    elif login_count >= 4 or time_span < interval:
        print('third condition Wait 30 minutes')
        return bad_request('Too many failed login attempts. PLease wait 30 minutes before signing in again.')
    # token = basic_auth.current_user().get_token()
    # db.session.commit()
    # return jsonify({'token': token})


@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204