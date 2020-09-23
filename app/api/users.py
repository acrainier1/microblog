from flask import jsonify, request, url_for, abort
# from flask_wtf import FlaskForm
from wtforms import validators
from wtforms.validators import Email
from wtforms.fields.html5 import EmailField
from app import db
from app.models import User, KanjiData
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request


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


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    print("data====\n", data)
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('Must include username, email and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('Please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('Please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    # response = jsonify(user.to_dict())
    response = jsonify({"statusCode": 201})
    response.status_code = 201
    # response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


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


@bp.route('/savemnemonic/<user>/<int:id>/<user_mnemonic>', methods=['POST'])
@token_auth.login_required
def save_mnemonic(user, id, mnemonic):
    pass
    # # ============ STATUS CODE ============
    # mnemonic = Mnemonics.query.get_or_404(id)
    # # ============ STATUS CODE ============
    # page = request.args.get('page', 1, type=int)
    # per_page = min(request.args.get('per_page', 10, type=int), 100)
    # data = User.to_collection_dict(user.followed, page, per_page,
    #                                'api.get_followed', id=id)
    # confirmation = ["Your menmonic device has been saved."]                            
    # return jsonify(confirmation)