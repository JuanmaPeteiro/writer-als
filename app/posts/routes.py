from flask import render_template, request, redirect
from app.posts import bp
import app
from uuid import uuid4
from werkzeug.utils import secure_filename
import os
from app import redis_instance

@bp.route('/')
def index():
    notes = getNotes()
    chapters = getChapters()
    for note in notes:
        note['chapters'] = [chapter for chapter in chapters if chapter['noteId'] == note['id']]
    return render_template('posts/index.html', notes=notes)

def getNotes():
    note_ids = app.redis_instance.keys('note:*')

    # Retrieve note data for each ID and store in a list
    notes = []
    for note_id in note_ids:
        note = app.redis_instance.hgetall(note_id)
        note = {key.decode('utf-8'): value.decode('utf-8') for key, value in note.items()}
        note['id'] = note_id.decode('utf-8')
        print(note)
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
    content = None
    for key, value in request.form.items():
        if key.startswith('content'):
            content = value
            break

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

@bp.route('/delete-chapter/<chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    print(f"Deleting chapter with key: {chapter_id}")

    if not app.redis_instance.exists(chapter_id):
        return "Chapter not found", 404

    # Delete the chapter from Redis
    app.redis_instance.delete(chapter_id)

    # Redirect the user to the note list page or any other appropriate page
    return redirect('/posts/')

@bp.route('/delete-note/<noteId>', methods=['POST'])
def delete_post(noteId):
    print(f"Deleting note with key: {noteId}")

    if not app.redis_instance.exists(noteId):
        return "Note not found", 404

    # Delete the chapter from Redis
    app.redis_instance.delete(noteId)

    # Redirect the user to the note list page or any other appropriate page
    return redirect('/posts/')




@bp.route('/add-note/', methods=['POST'])
def add_note():
    # Get the note title, content, image file, and categories from the form data
    redis_instance.ping()
    title = request.form.get('title')
    description = request.form.get('description')
    image = request.files['image']
    categories = request.form.getlist('categories')  # Get a list of selected categories
    print(categories)

    # Generate a unique ID for the note
    note_id = str(uuid4())

    # Save the note to Redis as a hash
    redis_instance.hset(f'note:{note_id}', 'title', title)
    redis_instance.hset(f'note:{note_id}', 'description', description)

    # Save the categories to Redis as a set
    for category in categories:
        redis_instance.sadd(f'note:{note_id}:categories', category)

    # Save the image file
    if image:
        filename = secure_filename(image.filename)
        upload_folder = os.path.join(bp.root_path, '..', 'static', 'upload')
        image.save(os.path.join(upload_folder, filename))
        redis_instance.hset(f'note:{note_id}', 'image', filename)

    # Redirect the user to the note list page
    return redirect('/posts/categories/')

