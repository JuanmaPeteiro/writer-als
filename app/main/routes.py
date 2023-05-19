from flask import render_template
from app.main import bp
from flask import render_template, request, redirect
from app.posts.routes import getNotes
import app
from uuid import uuid4

@bp.route('/')
def index():
    notes = getNotes()
    return render_template('index.html', notes=notes)
