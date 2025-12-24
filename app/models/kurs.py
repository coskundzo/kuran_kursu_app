from datetime import datetime
from app import db


class Kurs(db.Model):
    """Kurs Modeli"""
    __tablename__ = 'kurslar'
    
    id = db.Column(db.Integer, primary_key=True)
    adi = db.Column(db.String(200), nullable=False)
    kod = db.Column(db.String(50))
    adres = db.Column(db.Text)
    telefon = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Müftülük bilgisi
    muftu_id = db.Column(db.Integer, db.ForeignKey('muftulukler.id'))
    
    # Logo
    logo = db.Column(db.String(255))
    
    # Ayarlar
    ayarlar = db.Column(db.Text)  # JSON olarak saklanabilir
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    aktif = db.Column(db.Boolean, default=True)
    
    # Relationships
    ogrenciler = db.relationship('Ogrenci', backref='kurs', lazy='dynamic')
    egitmenler = db.relationship('Egitmen', backref='kurs', lazy='dynamic')
    siniflar = db.relationship('Sinif', backref='kurs', lazy='dynamic')
    
    def __repr__(self):
        return f'<Kurs {self.adi}>'


class Muftuluk(db.Model):
    """Müftülük Modeli"""
    __tablename__ = 'muftulukler'
    
    id = db.Column(db.Integer, primary_key=True)
    adi = db.Column(db.String(200), nullable=False)
    sehir = db.Column(db.String(100))
    bag = db.Column(db.Integer)  # Bağlı olduğu müftülük ID'si
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    aktif = db.Column(db.Boolean, default=True)
    
    # Relationships
    kurslar = db.relationship('Kurs', backref='muftuluk', lazy='dynamic')
    
    def __repr__(self):
        return f'<Muftuluk {self.adi}>'
