from app import db
from datetime import datetime


class KarneSablon(db.Model):
    """Karne Şablon Modeli"""
    __tablename__ = 'karne_sablonlar'
    
    id = db.Column(db.Integer, primary_key=True)
    adi = db.Column(db.String(200), nullable=False)
    arkaplan = db.Column(db.String(500))  # Arkaplan dosya yolu
    genislik = db.Column(db.Integer, default=800)  # px
    yukseklik = db.Column(db.Integer, default=1131)  # A4 oranı
    aktif = db.Column(db.Boolean, default=True)
    
    # İlişkiler
    kurs_id = db.Column(db.Integer, db.ForeignKey('kurslar.id'))
    kurs = db.relationship('Kurs', backref=db.backref('karne_sablonlari', lazy='dynamic'))
    
    # Şablon elemanları
    elemanlar = db.relationship('KarneSablonEleman', backref='sablon', lazy='dynamic', 
                               cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<KarneSablon {self.adi}>'


class KarneSablonEleman(db.Model):
    """Karne şablonundaki elemanlar (metin, değişken, ders vs.)"""
    __tablename__ = 'karne_sablon_elemanlari'
    
    id = db.Column(db.Integer, primary_key=True)
    sablon_id = db.Column(db.Integer, db.ForeignKey('karne_sablonlar.id'), nullable=False)
    
    # Eleman tipi: 'degisken', 'ders', 'sabit_metin'
    tip = db.Column(db.String(50), nullable=False)
    
    # Değişken adı (adsoyad, tc, sinif_adi vs.) veya ders_id
    anahtar = db.Column(db.String(200))
    
    # Sabit metin için
    metin = db.Column(db.String(500))
    
    # Konum bilgileri (px)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    
    # Stil bilgileri
    font_boyut = db.Column(db.Integer, default=14)
    font_renk = db.Column(db.String(20), default='#000000')
    font_stili = db.Column(db.String(50), default='normal')  # normal, bold, italic
    hizalama = db.Column(db.String(20), default='left')  # left, center, right
    genislik = db.Column(db.Integer, default=200)  # Metin kutusu genişliği
    
    sira = db.Column(db.Integer, default=0)  # Çizim sırası
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<KarneSablonEleman {self.tip}:{self.anahtar}>'
