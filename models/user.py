import uuid
from datetime import datetime, date
from flask_login import UserMixin, LoginManager
from mongoengine import Document, StringField, EmailField, DateTimeField, EmbeddedDocumentField
from main import app


login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(id):
    from storage.db import db_livechat
    return db_livechat.get_user(id=id)


class User(Document, UserMixin):
    uid = StringField(default=str(uuid.uuid4()))
    email = EmailField(required=True)
    created_at = DateTimeField(default=datetime.now())
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    password_hash = StringField(required=True)

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_password):
        from main import bcrypt
        self.password_hash = bcrypt.generate_password_hash(plain_password).decode('utf-8')

    def check_password(self, attempted_password):
        from main import bcrypt
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
        
    def __str__(self):
        return self.email

