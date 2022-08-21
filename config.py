import os

class Configuration(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI= 'postgresql://postgres:admin''@localhost:5433/flask_sispak'
    # SQLALCHEMY_DATABASE_URI= 'postgresql://dnpmchijbnrpuh:10b4f8b67eb7665e74ab76968895d304672190053ba030e98d554892871c7376@ec2-54-159-35-35.compute-1.amazonaws.com:5432/devftrilsbe4f7'
    SQLALCHEMY_TRACK_MODIFICATIONS = False