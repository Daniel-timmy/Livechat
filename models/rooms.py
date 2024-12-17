import uuid
from datetime import datetime
import random
from string import ascii_uppercase
from mongoengine import Document,ImageField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField, StringField, ReferenceField, ListField
from .user import User


def id_generator():
    code = "".join(random.choices(ascii_uppercase, k=6))
    return code

class Message(EmbeddedDocument):
    sender = ReferenceField(User)
    # attachment = ImageField()
    message = StringField()
    created_at = DateTimeField(default=datetime.now().strftime('%B %d, %H:%M'))
    

class Room(Document):
    uid = StringField(default=id_generator())
    name = StringField(required=True)
    description = StringField()
    created_at = DateTimeField()
    messages = ListField(EmbeddedDocumentField(Message))
    users = ListField(ReferenceField(User))
    # admin
