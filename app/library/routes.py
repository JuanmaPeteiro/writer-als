from flask import render_template, session
from app.library import bp
from app.main.routes import checkUser
from app.posts.routes import getNotes, getChapters


@bp.route('/')
def index():
    if (checkUser("user:" + session['user']) == 1):
        notes = getNotes()
        chapters = getChapters()
        for note in notes:
            note['chapters'] = [chapter for chapter in chapters if chapter['noteId'] == note['id']]
        return render_template('library/index.html', notes=notes)