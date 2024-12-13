import uuid
from datetime import datetime, date
from flask_login import UserMixin, LoginManager
from mongoengine import Document, StringField, EmailField, DateTimeField, EmbeddedDocumentField
from main import app


login_manager = LoginManager(app)

class User(Document, UserMixin):
    id = StringField(default=str(uuid.uuid4()))
    email = EmailField(required=True)
    created_at = DateTimeField(default=datetime.now())
    first_name = StringField(required=True)
    last_name = StringField(required=True)


    def __str__(self):
        return super().__str__()

@login_manager.user_loader
def load_user(user_id):
    pass
