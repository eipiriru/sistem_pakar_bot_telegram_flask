import os

class Configuration(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI= 'postgresql://postgres:admin''@localhost:5432/flask_sispak'
    SQLALCHEMY_DATABASE_URI= 'postgresql://wbpwadwqiwqawf:a2df7d4e664fd4426eb826222f5765b14150f1edfa4dc2423f7abfc7d0487992@ec2-44-209-186-51.compute-1.amazonaws.com:5432/du10148hs9eeh'
    SQLALCHEMY_TRACK_MODIFICATIONS = False