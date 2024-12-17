from models.user import User
from models.rooms import Room
from mongoengine import connect
from pymongo.errors import  ConfigurationError, ConnectionFailure


class DB:
    def __init__(self):
        try:
            print('nm,lkjnbnmkjnjn')
            password = 'fxz56BaCbxqTPVSk'
            connection_string = f'mongodb+srv://ajayi:{password}@livechatcluster.odmp3.mongodb.net/?retryWrites=true&w=majority&appName=LiveChatCluster'
            connect(db='LiveChat', host=connection_string)
            print('succesful connection')
        except (ConfigurationError, ConnectionFailure, Exception) as e:
            print(e)


    def get_user(self, id):
        user = User.objects(id=id)
        return user[0]

    def insert(self, obj):
        obj.save(obj)

    def get_user_by_email(self, email):
        if email is None:
            return None
        user = User.objects(email=email)
        if user:
            return User.objects(email=email)[0]

    def get_rooms(self, user):
        rooms = Room.objects(users=user)
        return rooms

    def get_room(self, room_uid):
        room = Room.objects(uid=room_uid).first()
        return room

    def add_message_to_room(self, room, sender, message_text, attachment=None):
        from models.rooms import Message
        # if not sender:
        #     raise AssertionError
        try:
            new_message = Message(sender=sender, message=message_text)
            room.messages.append(new_message)
            room.save()
        except Exception as e:
            print(e)

        print(f"Message added to room {room.uid}.")
    

db_livechat = DB()