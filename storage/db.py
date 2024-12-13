from models.user import User
from mongoengine import connect


class DB:
    def __init__(self):
        connection_string = ''
        connect(db='LiveChat', host=connection_string)
        print('succesful connection')

db_livechat = DB()