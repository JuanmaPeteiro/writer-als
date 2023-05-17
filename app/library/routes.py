from flask import render_template
from app.library import bp

@bp.route('/')
def index():
    return render_template('library/index.html')