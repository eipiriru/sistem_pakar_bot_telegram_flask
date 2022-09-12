import os

class Configuration(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI= 'postgresql://postgres:admin''@localhost:5432/flask_sispak'
    SQLALCHEMY_DATABASE_URI= 'postgresql://ilwhvjgrtpfugr:228c7b3436fe980d4573de38b35c48697ea52df15794a92b62ddbe4f9ad95c90@ec2-54-163-34-107.compute-1.amazonaws.com:5432/d6bm4ppfmigk35'
    SQLALCHEMY_TRACK_MODIFICATIONS = False