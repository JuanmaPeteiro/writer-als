import redis
from flask import render_template, request, redirect
from app.posts import bp
import app
from uuid import uuid4

@bp.route('/')
def index():
    notes = getNotes()
    return render_template('posts/index.html', notes=notes)

def getNotes():
    note_ids = app.redis_instance.keys('note:*')

    # Retrieve note data for each ID and store in a list
    notes = []
    for note_id in note_ids:
        note = app.redis_instance.hgetall(note_id)
        note = {key.decode('utf-8'): value.decode('utf-8') for key, value in note.items()}
        note['id'] = note_id.decode('utf-8')
        notes.append(note)
    return notes

def getChapters():
    chapter_ids = app.redis_instance.keys('chapter:*')

    # Retrieve chapter data for each ID and store in a list
    chapters = []
    for chapter_id in chapter_ids:
        chapter = app.redis_instance.hgetall(chapter_id)
        chapter = {key.decode('utf-8'): value.decode('utf-8') for key, value in chapter.items()}
        chapter['id'] = chapter_id.decode('utf-8')
        chapters.append(chapter)
    return chapters


@bp.route('/categories/')
def categories():
    notes = getNotes()
    chapters = getChapters()
    for note in notes:
        note['chapters'] = [chapter for chapter in chapters if chapter['noteId'] == note['id']]
    return render_template('posts/categories.html', notes=notes)

@bp.route('/add-chapter/', methods=['POST'])
def add_chapter():
    # Get the note title and content from the form data
    note_id = request.form.get('noteId')
    chapter_title = request.form.get('chapterTitle')
    content = request.form.get('content')

    # Check if required fields are not empty
    if not note_id or not chapter_title or not content:
        return "Missing required fields", 400

    # Generate a unique ID for the note
    chapter_id = str(uuid4())

    # Save the note to Redis as a hash
    app.redis_instance.hset(f'chapter:{chapter_id}', 'noteId', note_id)
    app.redis_instance.hset(f'chapter:{chapter_id}', 'chapterTitle', chapter_title)
    app.redis_instance.hset(f'chapter:{chapter_id}', 'content', content)

    # Redirect the user to the note list page
    return redirect('/posts/categories/')


@bp.route('/add-note/', methods=['POST'])
def add_note():
    # Get the note title and content from the form data
    app.redis_instance.ping()
    title = request.form.get('title')
    description = request.form.get('description')

    # Generate a unique ID for the note
    note_id = str(uuid4())

    # Save the note to Redis as a hash
    app.redis_instance.hset(f'note:{note_id}', 'title', title)
    app.redis_instance.hset(f'note:{note_id}', 'description', description)

    # Redirect the user to the note list page
    return redirect('/posts/categories/')
