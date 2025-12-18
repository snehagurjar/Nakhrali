from models import User, Address
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

def add_user(name, email, phone, location, password, dob, gender):
    if User.query.filter_by(email=email).first():
        return False

    user = User(
        name=name,
        email=email,
        phone=phone,
        location=location,
        password=generate_password_hash(password),
        dob=dob,
        gender=gender
    )

    db.session.add(user)
    db.session.commit()
    return True


def verify_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return user.id, user.name
    return None


def update_password(user_id, new_password):
    user = User.query.get(user_id)
    if not user:
        return False

    user.password = generate_password_hash(new_password)
    db.session.commit()
    return True


def get_all_users():
    return User.query.all()
