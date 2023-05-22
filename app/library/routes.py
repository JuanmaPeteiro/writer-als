from flask import render_template, session, request, redirect

import app
from app import redis_instance
from app.library import bp
from app.posts.routes import getNotes, getChapters


def checkExists(key):
    if redis_instance.exists(key):
        return 1
    return 0

@bp.route('/')
def index():
    if 'user' in session:
        if (checkExists("user:" + session['user']) == 1):
            notes = getNotes()
            chapters = getChapters()
            for note in notes:
                note['chapters'] = [chapter for chapter in chapters if chapter['noteId'] == note['id']]
            return render_template('library/index.html', notes=notes)
    return redirect('/')

@bp.route('/like-note', methods=['POST'])
def like_note():
    note_id = request.form.get('note_id')
    email = session['user']

    favemail = app.redis_instance.hget(note_id, 'fav')
    string_without_prefix = str(favemail)[2:-1]
    # Check if the note favorite already exists
    if string_without_prefix == email:
        # If it exists, delete the favorite
        app.redis_instance.hdel(note_id, 'fav')
    else:
        # If it doesn't exist, add the favorite
        app.redis_instance.hset(note_id, 'fav', email)

    # Redirect the user to the note list page
    return redirect('/library')
