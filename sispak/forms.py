from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, TextAreaField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from sispak.models import User, Gejala
from flask_login import current_user
import requests, json

from flask_wtf.file import FileField, FileAllowed, FileRequired
# from flask_uploads import UploadSet, IMAGES

# images = UploadSet('images', IMAGES)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    user_type = RadioField('Tipe Pengguna', choices=(['admin','Administrator'],['pakar','Pakar']), validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create User')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

class ProfilForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password')
    password2 = PasswordField('Repeat Password', validators=[EqualTo('password')])
    submit = SubmitField('Create User')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None and username.data != current_user.username:
            raise ValidationError('Please use a different username.')

class FormGejala(FlaskForm):
    kode = StringField('Kode Gejala', validators=[DataRequired()])
    gejala = StringField('Nama Gejala', validators=[DataRequired()])
    deskripsi = TextAreaField('Deskripsi')
    submit = SubmitField('Simpan')

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class FormPenyakit(FlaskForm):
    kode = StringField('Kode Penyakit', validators=[DataRequired()])
    penyakit = StringField('Nama Penyakit', validators=[DataRequired(), Length(min=1, max=50)])
    deskripsi = TextAreaField('Deskripsi', validators=[DataRequired()])
    penanganan = TextAreaField('Penanganan', validators=[DataRequired()])
    submit = SubmitField('Simpan')
    gejala = MultiCheckboxField('Gejala', coerce=int,)
    image = FileField('Contoh gambar penyakit', validators=[FileAllowed(['png', 'jpg'], 'Upload file gambar exstensi jpg / png!')])

# class FormBotConfig(FlaskForm):
#     token = StringField('Token Bot Telegram', validators=[DataRequired()])
#     submit = SubmitField('Simpan')

#     def validate_token(self, token):
#         url = "https://api.telegram.org/bot" + str(token.data) +"/getMe"
#         headers = {"Accept": "application/json"}
#         response = requests.post(url, headers=headers)
#         result = json.loads(response.text)
#         if not result['ok']:
#             raise ValidationError('Token Not Valid')
    