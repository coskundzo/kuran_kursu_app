from datetime import datetime, date
from app import db


class Ders(db.Model):
    """Ders Modeli"""
    __tablename__ = 'dersler'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Ders Bilgileri
    adi = db.Column(db.String(100), nullable=False)
    kurs_id = db.Column(db.Integer, db.ForeignKey('kurslar.id'), nullable=False)
    sinif_id = db.Column(db.Integer, db.ForeignKey('siniflar.id'))
    egitmen_id = db.Column(db.Integer, db.ForeignKey('egitmenler.id'))
    
    # Tarih ve Saat
    tarih = db.Column(db.Date, nullable=False, index=True)
    baslangic_saati = db.Column(db.Time)
    bitis_saati = db.Column(db.Time)
    
    # Ders Türü
    tur = db.Column(db.String(50))  # hafızlık, yüzüne, özel vb.
    konu = db.Column(db.Text)
    aciklama = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Ders {self.adi} - {self.tarih}>'


class HafizlikDers(db.Model):
    """Hafızlık Dersi Modeli"""
    __tablename__ = 'hafizlik_dersler'
    
    id = db.Column(db.Integer, primary_key=True)
    
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('ogrenciler.id'), nullable=False, index=True)
    egitmen_id = db.Column(db.Integer, db.ForeignKey('egitmenler.id'), nullable=False)
    
    tarih = db.Column(db.Date, nullable=False, default=date.today, index=True)
    
    # Ezber Bilgileri
    sure = db.Column(db.String(50))
    ayet_baslangic = db.Column(db.Integer)
    ayet_bitis = db.Column(db.Integer)
    sayfa_baslangic = db.Column(db.Integer)
    sayfa_bitis = db.Column(db.Integer)
    
    # Değerlendirme
    basari_durumu = db.Column(db.String(20))  # T=Tatil, H=Hasta, vb.
    puan = db.Column(db.Integer)  # 0-100 arası
    notlar = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ogrenci = db.relationship('Ogrenci', backref='hafizlik_dersleri')
    egitmen = db.relationship('Egitmen', backref='hafizlik_dersleri')
    
    def __repr__(self):
        return f'<HafizlikDers Öğrenci:{self.ogrenci_id} - {self.tarih}>'


class Yoklama(db.Model):
    """Yoklama Modeli"""
    __tablename__ = 'yoklamalar'
    
    id = db.Column(db.Integer, primary_key=True)
    
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('ogrenciler.id'), nullable=False, index=True)
    ders_id = db.Column(db.Integer, db.ForeignKey('dersler.id'))
    
    tarih = db.Column(db.Date, nullable=False, default=date.today, index=True)
    durum = db.Column(db.String(20), default='geldi')  # geldi, gelmedi, izinli, hasta
    
    # Mazeret
    mazeret = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'))
    
    def __repr__(self):
        return f'<Yoklama Öğrenci:{self.ogrenci_id} - {self.tarih}>'


class AidatHareket(db.Model):
    """Aidat Hareket Modeli"""
    __tablename__ = 'aidat_hareketleri'
    
    id = db.Column(db.Integer, primary_key=True)
    
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('ogrenciler.id'), nullable=False, index=True)
    kurs_id = db.Column(db.Integer, db.ForeignKey('kurslar.id'), nullable=False)
    
    # Aidat Bilgileri
    tutar = db.Column(db.Numeric(10, 2), nullable=False)
    donem = db.Column(db.String(50))  # 2024-2025 1.Dönem vb.
    aciklama = db.Column(db.Text)
    
    # Ödeme
    odendi = db.Column(db.Boolean, default=False)
    odeme_tarihi = db.Column(db.Date)
    odeme_sekli = db.Column(db.String(50))  # nakit, kredi kartı, havale
    
    # Vade
    vade_tarihi = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'))
    
    def __repr__(self):
        return f'<AidatHareket Öğrenci:{self.ogrenci_id} - {self.tutar}TL>'


class SinavSonuc(db.Model):
    """Sınav Sonucu Modeli"""
    __tablename__ = 'sinav_sonuclari'
    
    id = db.Column(db.Integer, primary_key=True)
    
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('ogrenciler.id'), nullable=False, index=True)
    sinav_id = db.Column(db.Integer, nullable=False)  # sinavlar tablosu
    
    puan = db.Column(db.Numeric(5, 2))
    notlar = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SinavSonuc Öğrenci:{self.ogrenci_id} Sınav:{self.sinav_id}>'
