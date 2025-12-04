from datetime import datetime, date
from app import db


class Egitmen(db.Model):
    """Eğitmen Modeli"""
    __tablename__ = 'egitmenler'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Kişisel Bilgiler
    adsoyad = db.Column(db.String(100), nullable=False, index=True)
    tc = db.Column(db.String(11), unique=True)
    dogum_tarihi = db.Column(db.Date)
    cinsiyet = db.Column(db.String(1))  # E=Erkek, K=Kadın
    
    # İletişim
    telefon = db.Column(db.String(20))
    email = db.Column(db.String(120))
    adres = db.Column(db.Text)
    
    # Kurs Bilgileri
    kurs_id = db.Column(db.Integer, db.ForeignKey('kurslar.id'), nullable=False, index=True)
    
    # Eğitim ve Branş
    brans = db.Column(db.String(100))  # Hafızlık, Tefsir, Arapça vb.
    egitim_durumu = db.Column(db.String(100))
    mezuniyet = db.Column(db.String(200))
    
    # İstihdam
    baslangic_tarihi = db.Column(db.Date)
    gorev = db.Column(db.String(100))
    ucret = db.Column(db.Numeric(10, 2))
    
    # Fotoğraf
    foto = db.Column(db.Integer)  # dosyalar tablosundaki ID
    
    # Durum
    durum = db.Column(db.String(20), default='aktif')  # aktif, pasif, ayrıldı
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ogrenciler = db.relationship('Ogrenci', backref='egitmen', lazy='dynamic')
    dersler = db.relationship('Ders', backref='egitmen', lazy='dynamic')
    
    def get_ogrenci_sayisi(self):
        """Eğitmenin öğrenci sayısını döndür"""
        return self.ogrenciler.filter_by(durum='aktif').count()
    
    def get_yas(self):
        """Eğitmenin yaşını hesapla"""
        if self.dogum_tarihi:
            today = date.today()
            return today.year - self.dogum_tarihi.year - (
                (today.month, today.day) < (self.dogum_tarihi.month, self.dogum_tarihi.day)
            )
        return None
    
    def to_dict(self):
        """JSON için sözlük döndür"""
        return {
            'id': self.id,
            'adsoyad': self.adsoyad,
            'telefon': self.telefon,
            'email': self.email,
            'brans': self.brans,
            'kurs_id': self.kurs_id,
            'ogrenci_sayisi': self.get_ogrenci_sayisi(),
            'durum': self.durum
        }
    
    def __repr__(self):
        return f'<Egitmen {self.adsoyad}>'
