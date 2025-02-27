from datetime import datetime, timedelta
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import secrets
import string
from time import time
from app import db, login_manager
from sqlalchemy.ext.hybrid import hybrid_property


class User(UserMixin, db.Model):
    """Model użytkownika aplikacji"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    avatar = db.Column(db.String(120), default='default.png')
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacje
    dashboards = db.relationship('Dashboard', backref='author', lazy='dynamic')
    data_sources = db.relationship('DataSource', backref='owner', lazy='dynamic')
    
    # Token resetowania hasła
    reset_password_token = db.Column(db.String(40), default=None)
    reset_password_expires = db.Column(db.DateTime, default=None)
    
    # Token potwierdzenia e-mail
    email_confirmation_token = db.Column(db.String(40), default=None)
    
    # Ustawienia użytkownika
    settings = db.relationship('UserSettings', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # Tworzenie domyślnych ustawień przy tworzeniu nowego użytkownika
        if self.settings is None:
            self.settings = UserSettings()
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """Weryfikacja hasła użytkownika"""
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_password_token(self):
        """Generuje token resetowania hasła"""
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(40))
        self.reset_password_token = token
        self.reset_password_expires = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()
        return token
    
    def verify_reset_password_token(self, token):
        """Weryfikuje token resetowania hasła"""
        if (self.reset_password_token is None or
                token != self.reset_password_token or
                self.reset_password_expires < datetime.utcnow()):
            return False
        return True
    
    def generate_email_confirmation_token(self):
        """Generuje token potwierdzenia adresu e-mail"""
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(40))
        self.email_confirmation_token = token
        db.session.commit()
        return token
    
    def confirm_email(self, token):
        """Potwierdza adres e-mail"""
        if self.email_confirmation_token is None or token != self.email_confirmation_token:
            return False
        self.email_confirmed = True
        self.email_confirmation_token = None
        db.session.commit()
        return True
    
    def generate_auth_token(self, expiration=3600):
        """Generuje token JWT dla API"""
        payload = {
            'id': self.id,
            'exp': time() + expiration
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    @staticmethod
    def verify_auth_token(token):
        """Weryfikuje token JWT i zwraca użytkownika"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return User.query.get(payload['id'])
        except jwt.ExpiredSignatureError:
            # Token wygasł
            return None
        except jwt.InvalidTokenError:
            # Nieprawidłowy token
            return None
    
    @hybrid_property
    def full_name(self):
        """Zwraca pełne imię i nazwisko"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def update_last_login(self):
        """Aktualizuje datę ostatniego logowania"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'


class UserSettings(db.Model):
    """Model ustawień użytkownika"""
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Preferencje interfejsu
    theme = db.Column(db.String(20), default='light')
    dashboard_layout = db.Column(db.String(20), default='grid')
    items_per_page = db.Column(db.Integer, default=10)
    
    # Preferencje powiadomień
    email_notifications = db.Column(db.Boolean, default=True)
    dashboard_sharing_notifications = db.Column(db.Boolean, default=True)