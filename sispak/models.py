from sispak import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sispak import login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    type = db.Column(db.Enum('admin','pakar',name='type'))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

relasi_tabel = db.Table('relasi', 
    db.Column('penyakit_id', db.ForeignKey('penyakit.id')),
    db.Column('gejala_id', db.ForeignKey('gejala.id'))
)

class Penyakit(db.Model):
    __tablename__ = 'penyakit'
    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(5), unique=True)
    penyakit = db.Column(db.String(50))
    deskripsi = db.Column(db.Text)
    penanganan = db.Column(db.Text)
    gejala = db.relationship("Gejala", secondary=relasi_tabel)

class Gejala(db.Model):
    __tablename__ = 'gejala'
    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(5), unique=True)
    gejala = db.Column(db.String(50))
    deskripsi = db.Column(db.Text)
    penyakit = db.relationship("Penyakit", secondary=relasi_tabel)