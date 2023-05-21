from flask import Flask
from config import Config
from flask_session import Session
import redis
import os

redis_instance = redis.Redis()

def create_app(config_class=Config):
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(config_class)
    app.config['UPLOAD_FOLDER'] = 'app/static/upload'
    app.config['SECRET_KEY']
    app.secret_key = os.urandom(24)
    app.redis = redis.Redis.from_url(app.config['REDIS_URL'])

    # Initialize Flask extensions here
    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.posts import bp as posts_bp
    app.register_blueprint(posts_bp, url_prefix='/posts', redis=app.redis)

    from app.library import bp as library_bp
    app.register_blueprint(library_bp, url_prefix='/library', redis=app.redis)


    @app.route('/test-redis')
    def test_redis():
        response = app.redis.ping()
        return f'Redis connection test: {response}'

    return app