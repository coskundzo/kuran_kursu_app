
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Optional



class AidatForm(FlaskForm):
    ogrenci_id = StringField('Öğrenci ID', validators=[DataRequired()])
    tutar = StringField('Tutar', validators=[DataRequired()])
    donem = StringField('Dönem')
    vade_tarihi = StringField('Vade Tarihi')
    odendi = BooleanField('Ödendi')
    aciklama = StringField('Açıklama')
    submit = BooleanField('Aidat Ekle')


class LoginForm(FlaskForm):
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    remember = BooleanField('Beni Hatırla')


class OgrenciForm(FlaskForm):
    adsoyad = StringField('Ad Soyad', validators=[DataRequired()])
    tc = StringField('TC Kimlik No')
    telefon = StringField('Telefon')
    yas = StringField('Yaş')
    submit = BooleanField('Öğrenci Ekle')


class EgitmenForm(FlaskForm):
    adsoyad = StringField('Ad Soyad', validators=[DataRequired()])
    tc = StringField('TC Kimlik No')
    telefon = StringField('Telefon')
    email = StringField('E-posta', validators=[Optional(), Email()])
    kurs_id = SelectField('Kurs', coerce=int, validators=[DataRequired()])
    brans = StringField('Branş')
    submit = SubmitField('Eğitmen Ekle')

class DersForm(FlaskForm):
    adi = StringField('Ders Adı', validators=[DataRequired()])
    kurs_id = SelectField('Kurs', coerce=int, validators=[DataRequired()])
    sinif_id = SelectField('Sınıf', coerce=lambda x: int(x) if x else None)
    egitmen_id = SelectField('Eğitmen', coerce=lambda x: int(x) if x else None)
    tur = StringField('Ders Türü')
    konu = StringField('Konu')
    aciklama = StringField('Açıklama')
    submit = SubmitField('Ders Ekle')
