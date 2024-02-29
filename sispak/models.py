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
    type_user = db.Column(db.Enum('admin','pakar',name='type'))

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
    penyakit = db.Column(db.String(100))
    deskripsi = db.Column(db.Text)
    penanganan = db.Column(db.Text)
    gejala = db.relationship("Gejala", secondary=relasi_tabel)
    data = db.Column(db.LargeBinary)
    rendered_data = db.Column(db.Text)

class Gejala(db.Model):
    __tablename__ = 'gejala'
    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(5), unique=True)
    gejala = db.Column(db.String(100))
    deskripsi = db.Column(db.Text)
    penyakit = db.relationship("Penyakit", secondary=relasi_tabel)

class UserTelegram(db.Model):
    __tablename__ = 'usertelegram'
    id = db.Column(db.Integer, primary_key=True)
    id_bot = db.Column(db.BigInteger, unique=True)
    username = db.Column(db.String(64))
    name = db.Column(db.String(64))
    history = db.relationship("HistoryDiagnosa", backref='history')

class HistoryDiagnosa(db.Model):
    __tablename__ = 'history_diagnosa'
    id = db.Column(db.Integer, primary_key=True)
    usertelegram_id = db.Column(db.Integer, db.ForeignKey('usertelegram.id',ondelete='CASCADE'))
    tanggal = db.Column(db.DateTime)
    proses = db.relationship("ProsesDiagnosa", backref='proses')
    hasil = db.Column(db.String(64))

class ProsesDiagnosa(db.Model):
    __tablename__ = 'proses_diagnosa'
    id = db.Column(db.Integer, primary_key=True)
    history_id = db.Column(db.Integer, db.ForeignKey('history_diagnosa.id',ondelete='CASCADE'))
    seq = db.Column(db.Integer)
    gejala = db.Column(db.String(64))
    respon = db.Column(db.String(9))


# class BotConfig(db.Model):
#     __tablename__ = 'bot_config'
#     id = db.Column(db.Integer, primary_key=True)
#     token = db.Column(db.String(255))