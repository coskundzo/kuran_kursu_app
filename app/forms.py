
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, Optional

class ToplantiForm(FlaskForm):
    konu = StringField('Konu', validators=[DataRequired()])
    tarih = DateField('Tarih', format='%Y-%m-%d', validators=[DataRequired()])
    aciklama = TextAreaField('Açıklama')
    submit = SubmitField('Kaydet')
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Optional



class AidatForm(FlaskForm):
    ogrenci_id = SelectField('Öğrenci', coerce=int, validators=[DataRequired()])
    tutar = StringField('Tutar', validators=[DataRequired()])
    donem = StringField('Dönem')
    vade_tarihi = StringField('Vade Tarihi')
    odendi = BooleanField('Ödendi')
    aciklama = StringField('Açıklama')
    submit = SubmitField('Aidat Ekle')


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
    submit = SubmitField('Ders Ekle')

class DersKonuForm(FlaskForm):
    ders_id = SelectField('Ders Seçiniz', coerce=lambda x: int(x) if x else None, validators=[DataRequired()])
    konu = StringField('Konu Adı', validators=[DataRequired()])
    aciklama = StringField('Açıklama')
    submit = SubmitField('Konu Ekle')

