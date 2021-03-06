from flask import jsonify, request, url_for, abort
import ssl
import base64
from app import db
from app.api import bp
from app.api.auth0 import AuthError, requires_auth
from app.api.auth import token_auth, basic_auth
from app.api.errors import bad_request
from app.auth.email import send_mail, send_password_reset_email
from app.models import User, KanjiData, CustomNotes


@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    # ============ STATUS CODE ============
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)


@bp.route('/users/<int:id>/followers', methods=['GET'])
@token_auth.login_required
def get_followers(id):
    # ============ STATUS CODE ============
    user = User.query.get_or_404(id)
    # ============ STATUS CODE ============
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.followers, page, per_page,
                                   'api.get_followers', id=id)
    return jsonify(data)


@bp.route('/users/<int:id>/followed', methods=['GET'])
@token_auth.login_required
def get_followed(id):
    # ============ STATUS CODE ============
    user = User.query.get_or_404(id)
    # ============ STATUS CODE ============
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.followed, page, per_page,
                                   'api.get_followed', id=id)
    return jsonify(data)


@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    # ============ STATUS CODE ============
    if token_auth.current_user().id != id:
        abort(403)
    # ============ STATUS CODE ============
    user = User.query.get_or_404(id)
    # ============ STATUS CODE ============
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())


''' 
    ======================================
    ======================================
    >>>>>>>>>> FRONT END ROUTES <<<<<<<<<<
    ======================================
    ======================================
'''
@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'email' not in data or 'password' not in data:
        return bad_request('Must include email and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('Please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('Please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    token = user.get_token()
    db.session.add(user)
    db.session.commit()
    response = jsonify({
        "token": token,
        "statusCode": 201
    })
    response.status_code = 201
    return response


@bp.route('/getuser', methods=['GET'])
@token_auth.login_required
def get_user_data():
    if token_auth.current_user().id:
        response = {
            'email' : token_auth.current_user().email,
            'username' : token_auth.current_user().username
        }
        response['statusCode'] = 201
        return jsonify(response)
    return jsonify({})
    

@bp.route('/updateuser', methods=['POST'])
@token_auth.login_required
def update_user_data():
    ''' DESTRUCTURE INCOMING DATA '''
    data = request.get_json()
    print('data =====\n', data)
    old_email = data.get('oldEmail')
    new_email = data.get('newEmail')
    old_username = data.get('oldUsername')
    new_username = data.get('newUsername')
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')

    if User.query.filter_by(email=old_email).first():
        user = User.query.filter_by(email=old_email).first()
    else:
        return bad_request('Something went wrong! Please try again')

    ''' UPDATE EMAIL ONLY '''
    if 'newEmail' in data and 'newUsername' not in data and 'newPassword' not in data:
        if new_email == '':
            return bad_request('Please enter an email address')
        elif token_auth.current_user().email != old_email:
            abort(403)

        if new_email and new_email != user.email and \
                User.query.filter_by(email=new_email).first():
            return bad_request('Email error')

    ''' UPDATE USERNAME ONLY '''
    if 'newUsername' in data:
        if new_username == '':
            return bad_request('Please enter a username')
        elif token_auth.current_user().username != old_username:
            abort(403)

        if new_username and new_username != user.username and \
                User.query.filter_by(username=new_username).first():
            return bad_request('Username error')

    ''' UPDATE PASSWORD ONLY '''
    if 'oldPassword' in data and 'newPassword' in data:
        if not user.check_password(old_password):
            # abort(403)
            return bad_request('Password error')
        user.set_password(new_password)

    ''' RETURN UPDATED DATA '''
    user.update_data(data, new_user=False)
    db.session.commit()
    response = user.new_data()
    response['statusCode'] = 201
    return jsonify(response)


@bp.route('/reset_password_email/<email>', methods=['GET'])
def reset_password_request(email):
    user = User.query.filter_by(email=email).first()
    if user:
        send_mail(user)
    return jsonify({"response": "placeholder string return"})


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('/savecustomnotes', methods=['POST'])
@requires_auth
def save_custom_notes():
    data = request.get_json()
    notes = data.get('notes')
    kanji = int(data.get('kanji'))
    encoded_user = request.headers.get('Finder')
    user = base64.b64decode(encoded_user).decode("utf-8")
    print(data)

    custom_notes = CustomNotes()
    existing_notes = CustomNotes.query.filter_by(User=user).filter_by(Kanji=kanji).first()
    if existing_notes is not None:
        existing_notes.set_notes(notes, user, kanji)
    else:
        custom_notes.set_notes(notes, user, kanji)
    db.session.commit()
    response = { "statusCode": 201 }
    return jsonify(response)


@bp.route('/fetchcustomnotes', methods=['POST'])
@requires_auth
def fetch_custom_notes():
    data = request.get_json()
    kanji = int(data.get('kanji'))
    encoded_user = request.headers.get('Finder')
    user = base64.b64decode(encoded_user).decode("utf-8")
    print(data)

    existing_notes = CustomNotes.query.filter_by(User=user).filter_by(Kanji=kanji).first()
    if existing_notes is not None:
        response = { "notes": existing_notes.Notes }
        print('existing_notes', existing_notes.Kanji, existing_notes.Notes)
    else:
        response = { "notes": '' }
    response['statusCode'] = 201
    return jsonify(response)


@bp.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@bp.route('/postcontactform/<subject>/<name>/<email>/<message>/<page>/<card>', methods=['POST'])
def postContactForm(subject, name, email, message, page, card):
    # with sqlite3.connect(DBPATH2) as conn:
    #     cursor = conn.cursor()
    #     INSERT_SQL = """ 
    #           INSERT INTO user_messages
                #     (Subject,
                #     Name,
                #     Email,
                #     Message,
                #     Page, Card)

                # VALUES (
                #     :subject,
                #     :name,
                #     :email,
                #     :message,
                #     :page,
                #     :card);
    #     """
    #     values = {
    #         "subject": subject,
    #         "name": name,
    #         "email": email,
    #         "message": message,
    #         "page": page,
    #         "card": card
    #     }
    #     cursor.execute(INSERT_SQL, values)
    return jsonify({"status": "success"})