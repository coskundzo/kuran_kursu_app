from datetime import datetime, date
from app import db


class Ogrenci(db.Model):
    """Öğrenci Modeli"""
    __tablename__ = 'ogrenciler'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Kişisel Bilgiler
    adsoyad = db.Column(db.String(100), nullable=False, index=True)
    tc = db.Column(db.String(11), unique=True, index=True)
    dogum_tarihi = db.Column(db.Date)
    dogum_yeri = db.Column(db.String(100))
    cinsiyet = db.Column(db.String(1))  # E=Erkek, K=Kız
    
    # İletişim
    telefon = db.Column(db.String(20))
    email = db.Column(db.String(120))
    adres = db.Column(db.Text)
    
    # Veli Bilgileri
    veli_adi = db.Column(db.String(100))
    veli_telefon = db.Column(db.String(20))
    veli_email = db.Column(db.String(120))
    
    # Kurs Bilgileri
    kurs_id = db.Column(db.Integer, db.ForeignKey('kurslar.id'), nullable=False, index=True)
    sinif_id = db.Column(db.Integer, db.ForeignKey('siniflar.id'))
    egitmen_id = db.Column(db.Integer, db.ForeignKey('egitmenler.id'))
    
    # Sicil ve Kayıt
    sicil_no = db.Column(db.String(50), unique=True, index=True)
    kayit_tarihi = db.Column(db.Date, default=date.today)
    durum = db.Column(db.String(20), default='aktif')  # aktif, mezun, ayrıldı
    
    # Eğitim Bilgileri
    egitim_turu = db.Column(db.String(50))  # hafızlık, yüzüne vb.
    donem = db.Column(db.String(50))
    
    # Fotoğraf
    foto = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    yoklamalar = db.relationship('Yoklama', backref='ogrenci', lazy='dynamic')
    aidat_hareketleri = db.relationship('AidatHareket', backref='ogrenci', lazy='dynamic')
    sinavlar = db.relationship('SinavSonuc', backref='ogrenci', lazy='dynamic')
    
    def get_yas(self):
        """Öğrencinin yaşını hesapla"""
        if self.dogum_tarihi:
            today = date.today()
            return today.year - self.dogum_tarihi.year - (
                (today.month, today.day) < (self.dogum_tarihi.month, self.dogum_tarihi.day)
            )
        return None
    
    def get_aidat_borc(self):
        """Öğrencinin aidat borcunu hesapla"""
        from sqlalchemy import func
        from app.models.ders import AidatHareket
        borc = db.session.query(
            func.sum(AidatHareket.tutar)
        ).filter(
            AidatHareket.ogrenci_id == self.id,
            AidatHareket.odendi == False
        ).scalar()
        return borc or 0
    
    def to_dict(self):
        """JSON için sözlük döndür"""
        return {
            'id': self.id,
            'adsoyad': self.adsoyad,
            'tc': self.tc,
            'telefon': self.telefon,
            'email': self.email,
            'kurs_id': self.kurs_id,
            'sinif_id': self.sinif_id,
            'sicil_no': self.sicil_no,
            'durum': self.durum,
            'yas': self.get_yas()
        }
    
    def __repr__(self):
        return f'<Ogrenci {self.adsoyad}>'
