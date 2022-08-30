import os

class Configuration(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI= 'postgresql://postgres:admin''@localhost:5433/flask_sispak'
    SQLALCHEMY_DATABASE_URI= 'postgresql://vnxokzeeezvopk:7094229a6e132194e45ab8c9c522c002449b05abe912ad68dc2c1e95e590d3ff@ec2-35-168-122-84.compute-1.amazonaws.com:5432/d3ot75sk7tvp6a'
    SQLALCHEMY_TRACK_MODIFICATIONS = False