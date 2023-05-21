from flask import render_template
from app.main import bp
from flask import render_template,session, request, redirect
from app.posts.routes import getNotes
from app import redis_instance
import bcrypt
import app
from uuid import uuid4

def logout():
    session.pop('user')         #session.pop('user') help to remove the session from the browser
    return redirect('/')



def checkUser(key):
    if redis_instance.exists(key):
        return 1


def checkLogin(email, password):
    # Retrieve the user's stored hashed password from Redis
    stored_password = app.redis_instance.hget(f'user:{email}', 'password')
    print(password)
    print(stored_password)
    string_without_prefix = str(stored_password)[2:-1]

    # Check if the stored password matches the entered password
    if string_without_prefix == password:
        # Passwords match, login successful
        return 1
    else:
        # Passwords don't match, login unsuccessful
        return 0


@bp.route('/', methods=['GET','POST'])
def login():
    if(request.method == 'POST'):
        email = request.form.get('email')
        password = request.form.get('password')
        check = checkLogin(email, password)
        if check == 1:
            session['user'] = email
            return redirect('/home')

    return render_template('login.html')

@bp.route('/register', methods=['GET','POST'])
def register():
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        app.redis_instance.hset(f'user:{email}', 'username', username)
        app.redis_instance.hset(f'user:{email}', 'password', password)
        app.redis_instance.hset(f'user:{email}', 'email', email)
        return render_template('login.html')
    return render_template('register.html')

@bp.route('/home')
def index():
    print(session['user'])
    if (checkUser("user:"+session['user']) == 1):
        notes = getNotes()
        return render_template('index.html', notes=notes)
    return render_template('login.html')