# redis_helper.py
from flask import Flask


def save_user(user_id, name, age, email):
    # Use the Redis client from the Flask app
    app = Flask(__name__)
    redis_client = app.redis

    # Store user data using Redis hashes
    redis_client.hset(f'user:{user_id}', 'name', name)
    redis_client.hset(f'user:{user_id}', 'age', age)
    redis_client.hset(f'user:{user_id}', 'email', email)

def get_user(user_id):
    # Use the Redis client from the Flask app
    app = Flask(__name__)
    redis_client = app.redis

    # Retrieve user data from Redis hashes
    user_data = redis_client.hgetall(f'user:{user_id}')
    return user_data

# Define other Redis helper functions as needed
