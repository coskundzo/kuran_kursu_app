from app import db
from datetime import datetime

class EgitmenPerformans(db.Model):
    __tablename__ = 'egitmen_performanslar'
    
    id = db.Column(db.Integer, primary_key=True)
    egitmen_id = db.Column(db.Integer, db.ForeignKey('egitmenler.id'), nullable=False)
    yil = db.Column(db.Integer, nullable=False)
    ay = db.Column(db.Integer, nullable=False)
    kriter = db.Column(db.String(500), nullable=False)
    hafta1 = db.Column(db.Integer, default=0)
    hafta2 = db.Column(db.Integer, default=0)
    hafta3 = db.Column(db.Integer, default=0)
    hafta4 = db.Column(db.Integer, default=0)
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    egitmen = db.relationship('Egitmen', backref=db.backref('performanslar', lazy=True))
    
    def __repr__(self):
        return f'<EgitmenPerformans {self.egitmen_id} - {self.yil}/{self.ay} - {self.kriter}>'
    
    def toplam_puan(self):
        """Tüm haftaların toplam puanı"""
        return self.hafta1 + self.hafta2 + self.hafta3 + self.hafta4
    
    def ortalama_puan(self):
        """4 haftanın ortalaması"""
        toplam = self.toplam_puan()
        return round(toplam / 4, 2) if toplam > 0 else 0
