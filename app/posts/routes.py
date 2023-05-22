from flask import render_template, request, redirect, session

from app.posts import bp
import app
from uuid import uuid4
from werkzeug.utils import secure_filename
import os
from app import redis_instance

def checkUser(key):
    if redis_instance.exists(key):
        return 1
    return 0

@bp.route('/')
def index():
    if 'user' in session:
        if (checkUser("user:" + session['user']) == 1):
            notes = getUserNotes()
            chapters = getUserChapters()
            for note in notes:
                note['chapters'] = [chapter for chapter in chapters if chapter['noteId'] == note['id']]
            return render_template('posts/index.html', notes=notes)
    return redirect('/')

def getUserNotes():
    note_ids = app.redis_instance.keys('note:*')

    # Retrieve note data for each ID and store in a list
    notes = []
    for note_id in note_ids:
        note = app.redis_instance.hgetall(note_id)
        note = {key.decode('utf-8'): value.decode('utf-8') for key, value in note.items()}
        email = note.get('email')  # Retrieve the email value using the get method

        # Check if the email field exists and matches the session user
        if email and email == session['user']:
            note['id'] = note_id.decode('utf-8')
            notes.append(note)
    return notes

def getUserNotesLiked():
    note_ids = app.redis_instance.keys('note:*')

    # Retrieve note data for each ID and store in a list
    notes = []
    for note_id in note_ids:
        note = app.redis_instance.hgetall(note_id)
        note = {key.decode('utf-8'): value.decode('utf-8') for key, value in note.items()}
        email = note.get('fav')  # Retrieve the email value using the get method

        # Check if the email field exists and matches the session user
        if email and email == session['user']:
            note['id'] = note_id.decode('utf-8')
            notes.append(note)
    return notes

def getMostLiked():
    note_ids = app.redis_instance.keys('note:*')

    # Retrieve note data for each ID and store in a list
    notes = []
    for note_id in note_ids:
        note = app.redis_instance.hgetall(note_id)
        note = {key.decode('utf-8'): value.decode('utf-8') for key, value in note.items()}
        note['id'] = note_id.decode('utf-8')

        notes.append(note)

    # Count the occurrences of 'fav' in each note
    note_counts = []
    for note in notes:
        fav_count = note.get('fav', '').count(note.get('fav', ''))
        note_counts.append((note['id'], fav_count))

    # Sort notes based on the count of 'fav' in descending order
    sorted_notes = sorted(note_counts, key=lambda x: x[1], reverse=True)

    # Get the IDs of the top three notes
    top_three_ids = [note[0] for note in sorted_notes[:4]]

    notes = [note for note in notes if note['id'] in top_three_ids]

    return notes




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

def getUserChapters():
    chapter_ids = app.redis_instance.keys('chapter:*')

    # Retrieve chapter data for each ID and store in a list
    chapters = []
    for chapter_id in chapter_ids:
        chapter = app.redis_instance.hgetall(chapter_id)
        chapter = {key.decode('utf-8'): value.decode('utf-8') for key, value in chapter.items()}
        email = chapter.get('email')  # Retrieve the email value using the get method

        # Check if the email field exists and matches the session user
        if email and email == session['user']:
            chapter['id'] = chapter_id.decode('utf-8')
            chapters.append(chapter)
    return chapters

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
    if 'user' in session:
        if (checkUser("user:"+session['user']) == 1):
            notes = getUserNotes()
            chapters = getUserChapters()

            likednotes = getUserNotesLiked()

            for note in notes:
                note['chapters'] = [chapter for chapter in chapters if chapter['noteId'] == note['id']]
            for likednote in likednotes:
                likednote['chapters'] = [chapter for chapter in chapters if chapter['noteId'] == likednote['id']]
            return render_template('posts/categories.html', notes=notes, likednotes=likednotes)
    return redirect('/')

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

    # Save the user email as a key in the note
    email = session['user']
    app.redis_instance.hset(f'chapter:{chapter_id}', 'email', email)

    # Save the note to Redis as a hash
    app.redis_instance.hset(f'chapter:{chapter_id}', 'noteId', note_id)
    app.redis_instance.hset(f'chapter:{chapter_id}', 'chapterTitle', chapter_title)
    app.redis_instance.hset(f'chapter:{chapter_id}', 'content', content)

    # Redirect the user to the note list page
    return redirect('/posts/')

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

    # Generate a unique ID for the note
    note_id = str(uuid4())

    # Save the note to Redis as a hash
    redis_instance.hset(f'note:{note_id}', 'title', title)
    redis_instance.hset(f'note:{note_id}', 'description', description)

    # Save the user email as a key in the note
    email = session['user']
    app.redis_instance.hset(f'note:{note_id}', 'email', email)

    # Save the categories as a list within the note's hash structure
    redis_instance.hset(f'note:{note_id}', 'categories', ','.join(categories))

    # Save the image file
    if image:
        filename = secure_filename(image.filename)
        upload_folder = os.path.join(bp.root_path, '..', 'static', 'upload')
        image.save(os.path.join(upload_folder, filename))
        redis_instance.hset(f'note:{note_id}', 'image', filename)

    # Redirect the user to the note list page
    return redirect('/posts/')

@bp.route('/edit-note/', methods=['POST'])
def edit_note():
    # Get the note ID from the form data
    note_id = request.form.get('note_id')

    # Get the existing note data from Redis
    note_data = redis_instance.hgetall(note_id)

    # Get the updated note title, description, and categories from the form data
    title = request.form.get('title')
    description = request.form.get('descriptionEdit')
    categories = request.form.getlist('categories')  # Get a list of selected categories

    # Update the note data in Redis with the new values
    redis_instance.hset(note_id, 'title', title)
    redis_instance.hset(note_id, 'description', description)
    redis_instance.hset(note_id, 'categories', ','.join(categories))

    # Update the image file if a new file is received
    image = request.files['image']

    if image:
        # Delete the existing image file, if any
        existing_image = note_data.get(b'image')
        if existing_image:
            existing_image_path = os.path.join(bp.root_path, '..', 'static', 'upload', existing_image.decode())
            if os.path.exists(existing_image_path):
                os.remove(existing_image_path)

        # Save the new image file
        filename = secure_filename(image.filename)
        upload_folder = os.path.join(bp.root_path, '..', 'static', 'upload')
        image.save(os.path.join(upload_folder, filename))
        redis_instance.hset(note_id, 'image', filename)

    # Redirect the user to the note list page
    return redirect('/posts/')



