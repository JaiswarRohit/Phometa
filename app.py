import uuid
from datetime import datetime, timedelta
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash


phometa = Flask(__name__)

phometa.config['SECRET_KEY'] = ')?/~%^&*(@3[0#]'
phometa.config['JWT_SECRET_KEY'] = '&*(@3[0#])?/~%^'
phometa.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
phometa.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5432/Phometa'


db = SQLAlchemy(phometa)
migrate = Migrate(phometa, db)

api = Api(phometa)
jwt = JWTManager(phometa)


class User(db.Model):
    id = db.Column(db.String(36), nullable=False, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    pass_hash = db.Column(db.String(300), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.now)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    def set_pass(self, passwd):
        self.pass_hash = generate_password_hash(passwd)

    def check_pass(self, passwd):
        return check_password_hash(self.pass_hash, passwd)


class ContactBook(db.Model):
    id = db.Column(db.String(36), nullable=False, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'))
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)


class SpamNumbers(db.Model):
    id = db.Column(db.String(36), nullable=False, primary_key=True, default=uuid.uuid4)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    mark_count = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)


class UserSpamFlags(db.Model):
    id = db.Column(db.String(36), nullable=False, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'))
    mark_id = db.Column(db.String(36), db.ForeignKey('spam_numbers.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)


class TokenInvoked(db.Model):
    id = db.Column(db.String(36), nullable=False, primary_key=True, default=uuid.uuid4)
    token_identifier = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)


@jwt.token_in_blocklist_loader
def check_revoked_token(jwt_header, jwt_payload: dict) -> bool:
    token_identifier = jwt_payload["jti"]
    token = TokenInvoked.query.filter_by(token_identifier=token_identifier).first()
    return token is not None


class Register(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True)
    parser.add_argument('phone', type=str, required=True)
    parser.add_argument('email', type=str, required=True)
    parser.add_argument('password', type=str, required=True)

    def post(self):
        try:
            data = Register.parser.parse_args()

            if User.query.filter_by(phone=data.get('phone')).first():
                return {'message': 'Phone already exists.'}, 400
            if data.get('email'):
                if User.query.filter_by(email=data.get('email')).first():
                    return {'message': 'Email already exists.'}, 400

            user = User(name=data.get('name'), phone=data.get('phone'), email=data.get('email'))
            user.set_pass(data.get('password'))
            db.session.add(user)
            db.session.commit()

            return {'message': 'User created successfully.'}, 201

        except Exception as e:
            print(f"ERROR = {e}")
            return {'message': 'Something went Wrong.'}, 500


class Login(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('phone', type=str, required=True)
    parser.add_argument('password', type=str, required=True)

    def post(self):
        try:
            data = Login.parser.parse_args()
            user = User.query.filter_by(phone=data.get('phone')).first()
            if user and user.check_pass(data.get('password')):
                user.last_login = datetime.now()
                db.session.commit()
                access_token = create_access_token(identity=data.get('phone'))
                return {'access_token': access_token}, 200
            return {'message': 'Invalid username or password. Please try again.'}, 400

        except Exception as e:
            print(f"ERROR = {e}")
            return {'message': 'Something went Wrong.'}, 500


class Logout(Resource):

    @jwt_required()
    def post(self):
        try:
            token_identifier = get_jwt()
            token_invoked = TokenInvoked(token_identifier=token_identifier.get("jti"))
            db.session.add(token_invoked)
            db.session.commit()
            return {"msg": "User logged out successfully. Token Expired."}, 201

        except Exception as e:
            print(f"ERROR = {e}")
            return {'message': 'Something went Wrong.'}, 500


class AddContact(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True)
    parser.add_argument('phone', type=str, required=True)

    @jwt_required()
    def post(self):
        try:
            data = AddContact.parser.parse_args()
            user = User.query.filter_by(phone=get_jwt_identity()).first()

            if ContactBook.query.filter_by(phone=data.get('phone'), user_id=user.id).first():
                return {'message': 'Phone number already in contact book.'}, 400

            contact = ContactBook(name=data.get('name'), phone=data.get('phone'), user_id=user.id)
            db.session.add(contact)
            db.session.commit()

            return {'message': 'Contact added successfully.'}, 201

        except Exception as e:
            print(f"ERROR = {e}")
            return {'message': 'Something went Wrong.'}, 500


class MarkSpam(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('phone', type=str, required=True)

    @jwt_required()
    def post(self):
        try:
            data = MarkSpam.parser.parse_args()
            user = User.query.filter_by(phone=get_jwt_identity()).first()
            spam_number = SpamNumbers.query.filter_by(phone=data.get('phone')).first()

            if spam_number:
                spam_flag = UserSpamFlags.query.filter_by(user_id=user.id, mark_id=spam_number.id).first()
                if spam_flag:
                    return {'message': 'Number already marked as spam.'}, 201

                else:
                    spam_flag = UserSpamFlags(user_id=user.id, mark_id=spam_number.id)
                    spam_number.mark_count += 1
                    db.session.add(spam_flag)
                    db.session.commit()

                    return {'message': 'Number marked as spam.'}, 201

            spam_number = SpamNumbers(phone=data.get('phone'))
            db.session.add(spam_number)
            db.session.flush()

            spam_flag = UserSpamFlags(user_id=user.id, mark_id=spam_number.id)
            db.session.add(spam_flag)
            db.session.flush()

            db.session.commit()

            return {'message': 'Number marked as spam.'}, 201

        except Exception as e:
            print(f"ERROR = {e}")
            return {'message': 'Something went Wrong.'}, 500


class SearchUser(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=False)
    parser.add_argument('phone', type=str, required=False)

    @jwt_required()
    def post(self):
        try:
            data = SearchUser.parser.parse_args()
            curr_user = User.query.filter_by(phone=get_jwt_identity()).first()

            users = None
            if data.get('name'):
                users = User.query.filter(User.name.like(f"%{data.get('name')}%")).all()
            elif data.get('phone'):
                users = User.query.filter_by(phone=data.get('phone')).all()
            details, contact_names = list(), list()
            if users:
                for user in users:
                    spam_number = SpamNumbers.query.filter_by(phone=user.phone).first()
                    spam_reports = spam_number.mark_count if spam_number else 0
                    temp = {
                        "name": user.name,
                        "phone": user.phone,
                        "spam_reports": spam_reports,
                    }
                    contact = ContactBook.query.filter_by(phone=user.phone, user_id=curr_user.id).first()
                    if contact:
                        temp.update({
                            "contact_name": contact.name,
                            "email": user.email
                        })
                    details.append(temp)

            elif SpamNumbers.query.filter_by(phone=data.get('phone')).first():
                spam_number = SpamNumbers.query.filter_by(phone=data.get('phone')).first()
                if spam_number:
                    temp = {
                        "phone": spam_number.phone,
                        "spam_reports": spam_number.mark_count,
                    }
                    contact = ContactBook.query.filter_by(phone=data.get('phone'), user_id=curr_user.id).first()
                    if contact:
                        temp.update({
                            "contact_name": contact.name
                        })
                    details.append(temp)

            elif ContactBook.query.filter_by(phone=data.get('phone')).first():
                contact = ContactBook.query.filter_by(phone=data.get('phone'), user_id=curr_user.id).first()
                if contact:
                    temp = {
                        "phone": data.get('phone'),
                        "contact_names": contact.name,
                        "spam_reports": 0,
                    }
                    details.append(temp)

            if details:
                return {'message': f"{len(details)} User(s) Found", "data": details}, 201
            return {'message': 'No Users Found'}, 404

        except Exception as e:
            print(f"ERROR = {e}")
            return {'message': 'Something went Wrong.'}, 500


api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(MarkSpam, '/mark-spam')
api.add_resource(AddContact, '/add-contact')
api.add_resource(SearchUser, '/search')
api.add_resource(Logout, '/logout')


if __name__ == '__main__':
    phometa.run()
