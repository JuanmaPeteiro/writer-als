import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'redbubblefish'
    REDIS_URL = 'redis://localhost:6379/0'