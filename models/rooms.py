import uuid
from datetime import datetime
import random
from string import ascii_uppercase
from mongoengine import Document, DateTimeField, EmbeddedDocument, EmbeddedDocumentField, StringField, ReferenceField, ListField
from user import User


def id_generator():
    code = "".join(random.choices(ascii_uppercase, k=6))
    return code

class Message(EmbeddedDocument):
    sender = ReferenceField(User)
    message = StringField()
    created_at = DateTimeField(default=datetime.now())

class Room(Document):
    id = StringField(default=id_generator())
    name = StringField(required=True)
    description = StringField()
    created_at = DateTimeField()
    messages = ListField(EmbeddedDocumentField(Message))
    user = ListField(ReferenceField(User))
    # admin
