from flask import Flask, render_template, request, session, redirect, url_for, current_app
from flask_socketio import join_room, leave_room, send, SocketIO, emit
import random
from string import ascii_uppercase
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
import uuid
import wave

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config["SECRET_KEY"] = "mysecret"
login_manager = LoginManager(app)
socketio = SocketIO(app)
login_manager.login_view = 'login'
rooms = {}
app.config['FILEDIR'] = 'static/files/'

@login_manager.user_loader
def load_user(user_id):
    from storage.db import db_livechat
    return db_livechat.get_user(id=user_id)

def generate_unique_code(length):
    from storage.db import db_livechat
    code = "".join(random.choices(ascii_uppercase, k=length))
    if code in rooms:
        return generate_unique_code(length)
    return code

def user_confirmation(email, password):
    from storage.db import db_livechat
    try:
        requested_user = db_livechat.get_user_by_email(email=email)
        if requested_user:
            if requested_user.check_password(password):
                return requested_user
    except Exception:
        return None

@app.route('/login', methods=['POST', 'GET'])
def login():
    from storage.db import db_livechat
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        print(request.form)
        if not email:
            return render_template("login.html", error="Please enter your email", email=email, password=password)
        if not password:
            return render_template('login.html', error="Please enter your password", email=email, password=password)

        user = user_confirmation(email=email, password=password)

        if user:
            login_user(user)
            rooms = db_livechat.get_rooms(current_user)
            return redirect(url_for('home', rooms=rooms))
        else:
            return render_template('login.html', error="User can not be found", email=email, password=password)
        
    return render_template("login.html")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    from models.user import User
    from storage.db import db_livechat

    if request.method == "POST":
        print(request.form)
        email = request.form.get("email")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not email or not first_name or not last_name or not password or not confirm_password:
            return render_template("signup.html", error="Please fill in all fields",
                                   email=email, first_name=first_name, last_name=last_name)

        if db_livechat.get_user_by_email(email=email):
           return render_template("signup.html", error="User with that email already exists",
                                   email=email, first_name=first_name, last_name=last_name)
        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match",
                                   email=email, first_name=first_name, last_name=last_name)
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(email=email, first_name=first_name,
                     last_name=last_name, password_hash=password_hash)
        if user:
            db_livechat.insert(user)
            login_user(user)
            rooms = db_livechat.get_rooms(current_user)
            return redirect(url_for('home', rooms=rooms))
        else:
            render_template("signup.html", error="Failed to register user")
    return render_template("signup.html")
        

@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return render_template("logout.html")

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template("index.html")

@app.route('/home', methods=["POST", "GET"])
@login_required
def home():
    from storage.db import db_livechat

    rooms = db_livechat.get_rooms(current_user)
    return render_template("home.html", rooms=rooms, unread_messages=14)

@app.route('/enter/<room_uid>/<name>', methods=['POST', 'GET'])
@login_required
def enter(room_uid, name):
    # session.clear()
    session['room'] = [room_uid, name]
    if room_uid not in rooms:

        rooms[room_uid] = {"members": 0}
    return redirect(url_for("room", room_uid=room_uid, name=name))

@app.route('/create', methods=['POST', 'GET'])
@login_required
def create():
    from storage.db import db_livechat
    from models.rooms import Room
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        if not name:
            return render_template('create.html',
                                   error='Please enter a name for the room', name=name, description=description)
        if not description:
            return render_template('create.html',
                                   error='Please enter a name for the room', name=name, description=description)
        room = Room(name=name, description=description)
        room.users.append(current_user)
        print(room.uid)
        db_livechat.insert(room)
        session['room'] = [room.uid, name]
        rooms[room.uid] = {"members": 0}
        return redirect(url_for("room", room_uid=room.uid, name=room.name))

    return render_template('create.html')

@app.route('/join', methods=["POST", "GET"])
@login_required
def join():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)

        if not name:
            return render_template("join.html", error="Please enter your name", code=code, name=name)

        if not code:
            return render_template("join.html", error="Please enter a room code", code=code, name=name)

        room_uid = code

        session['room'] = [room_uid, name]
        if join:
            if room_uid not in rooms:
                rooms[room_uid] = {"members": 0}
        return redirect(url_for("room", room_id=room_uid, name=name))
    return render_template("join.html")

@app.route('/room/<room_uid>/<name>')
@login_required
def room(room_uid, name):
    from storage.db import db_livechat
    [room_id, room_name] = session.get('room')
    if room_id is None:
        return render_template('room.html', code=room_id, messages=[], error='Room code not found')
    room = db_livechat.get_room(room_uid=room_id)
    print(f'ROOM {room}')
    if not room:
        return render_template('room.html', code=room_id, messages=[], error='Room not found')
    messages = room.messages
    print(f'room messages {messages}')
    return render_template('room.html', code=room_id, messages=messages)



@socketio.on('connect')
def connect(auth):
    room_id, name = session.get('room')
    if not room_id or not name:
        return
    # if  room_id not in rooms:
    #     leave_room(room_id)
    #     return
    join_room(room_id)
    print(f"{name} connected to room {room_id}")
    send({'name': name, 'message': "has entered the room", 'date': str(datetime.now().strftime('%B %d, %H:%M'))}, to=room_id)
    print(rooms[room_id]['members'])
    rooms[room_id]['members'] += 1
    print(f"{name} joined room {room_id}")

@socketio.on('disconnect')
def disconnect():

    room_id, name = session.get('room')
    leave_room(room)

    if room_id in rooms:
        rooms[room_id]['members'] -= 1
        if rooms[room_id]['members'] <= 0:
            del rooms[room_id]

    send({"name": name, "message": "has left the room"}, to=room_id)
    print(f'{name} has left the room {room_id}')


@socketio.on('message')
def message(data):
    from storage.db import db_livechat

    room_id, name = session.get('room')
    print(f'room_id: {room_id} rooms: {rooms}')
    # if room_id not in rooms:
    #     return
    room = db_livechat.get_room(room_id)
    if not room:
        print(f"Room with uid {room_id} not found.")
        return

    content = {
        "name": name,
        "message": data['data'],
        'date': str(datetime.now())
    }
    send(content, to=room.uid)
    db_livechat.add_message_to_room(room, current_user, data['data'])

    print(f"{content['name']} sent {content['message']} to room {room_id}")


if __name__ == "__main__":
    socketio.run(app, debug=True)