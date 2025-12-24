from datetime import datetime
from app import db


class Sinif(db.Model):
    """Sınıf Modeli"""
    __tablename__ = 'siniflar'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Sınıf Bilgileri
    adi = db.Column(db.String(100), nullable=False)
    kod = db.Column(db.String(50))
    kurs_id = db.Column(db.Integer, db.ForeignKey('kurslar.id'), nullable=False)
    egitmen_id = db.Column(db.Integer, db.ForeignKey('egitmenler.id'))
    
    # Seviye ve Tür
    seviye = db.Column(db.String(50))  # Başlangıç, Orta, İleri
    tur = db.Column(db.String(50))  # Hafızlık, Tecvid, Yüzüne vb.
    
    # Kapasite
    kontenjan = db.Column(db.Integer, default=15)
    
    # Ders Saatleri
    ders_gunleri = db.Column(db.String(200))  # Pazartesi, Çarşamba, Cuma
    ders_saati = db.Column(db.String(50))  # 09:00-11:00
    
    # Açıklama
    aciklama = db.Column(db.Text)
    
    # Durum
    aktif = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ogrenciler = db.relationship('Ogrenci', backref='sinif', lazy='dynamic')
    dersler = db.relationship('Ders', backref='sinif', lazy='dynamic')
    
    def __repr__(self):
        return f'<Sinif {self.adi}>'
    
    @property
    def mevcud_ogrenci_sayisi(self):
        """Sınıftaki aktif öğrenci sayısı"""
        return self.ogrenciler.filter_by(durum='aktif').count()
    
    @property
    def bos_kontenjan(self):
        """Boş kontenjan"""
        if self.kontenjan is None:
            return 0
        return self.kontenjan - self.mevcud_ogrenci_sayisi
    
    @property
    def doluluk_orani(self):
        """Doluluk oranı yüzde olarak"""
        if self.kontenjan and self.kontenjan > 0:
            return round((self.mevcud_ogrenci_sayisi / self.kontenjan) * 100, 1)
        return 0
