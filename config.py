import os

class Configuration(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI= 'postgresql://postgres:admin''@localhost:5433/flask_sispak'
    SQLALCHEMY_DATABASE_URI= 'postgresql://://atloircgbltpxw:d76c722d51517458e8165432b5821abc948dbf7cb2349c2c01e78d1b9798e169@ec2-3-211-221-185.compute-1.amazonaws.com:5432/dfcuc71g20dt38'
    SQLALCHEMY_TRACK_MODIFICATIONS = False