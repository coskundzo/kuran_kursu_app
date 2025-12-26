from datetime import datetime, date
from app import db


class OgrenciPerformans(db.Model):
    """Öğrenci Performans Modeli"""
    __tablename__ = 'ogrenci_performanslar'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # İlişkiler
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('ogrenciler.id'), nullable=False, index=True)
    kurs_id = db.Column(db.Integer, db.ForeignKey('kurslar.id'), nullable=False)
    sinif_id = db.Column(db.Integer, db.ForeignKey('siniflar.id'))
    
    # Tarih ve Tür
    tarih = db.Column(db.Date, nullable=False, default=date.today)
    veri_turu = db.Column(db.String(20), default='gunluk')  # gunluk, haftalik
    
    # ÖĞRENCİ BAŞARI - Performans Puanları
    ders_calisma_disiplini = db.Column(db.Integer, default=0)
    ders_verme_performansi = db.Column(db.Integer, default=0)
    sistem_uygulanma_disiplini = db.Column(db.Integer, default=0)
    ders_okuyus_hizi = db.Column(db.Integer, default=0)
    talim_tecvid_durumu = db.Column(db.Integer, default=0)
    ders_verme_zamanlamasi = db.Column(db.Integer, default=0)
    sayfa_dinleme_disiplini = db.Column(db.Integer, default=0)
    kuran_kulturune_uyum = db.Column(db.Integer, default=0)
    hafta_basinda_kurs_zamanlamasi_giris = db.Column(db.Integer, default=0)
    ders_saatlerinde_sinifa_zamanlama_giris_mutabaa_saatleri = db.Column(db.Integer, default=0)
    
    # ÖĞRENCİ DAVRANIŞ - Davranış Puanları  
    kultur_saatlari_ders_zamanlama_giris = db.Column(db.Integer, default=0)
    sinif_hoca_ile_iletisim = db.Column(db.Integer, default=0)
    arkadaslariyla_iletisim = db.Column(db.Integer, default=0)
    namaz_vakitlerinde_mescide_zamanlama_giris = db.Column(db.Integer, default=0)
    ibadet_disiplini = db.Column(db.Integer, default=0)
    kilkiyafet_disiplini = db.Column(db.Integer, default=0)
    yeme_icme_disiplini = db.Column(db.Integer, default=0)
    yatalakhane_disiplini = db.Column(db.Integer, default=0)
    trafic_kontrolu_kendini_cikisine_becerisi_temizlik_ve_duzen = db.Column(db.Integer, default=0)
    genel_disiplin = db.Column(db.Integer, default=0)
    
    # Notlar
    notlar = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    ogrenci = db.relationship('Ogrenci', backref='performanslar')
    
    def toplam_basari_puani(self):
        """Toplam başarı puanını hesapla"""
        return (
            self.ders_calisma_disiplini +
            self.ders_verme_performansi +
            self.sistem_uygulanma_disiplini +
            self.ders_okuyus_hizi +
            self.talim_tecvid_durumu +
            self.ders_verme_zamanlamasi +
            self.sayfa_dinleme_disiplini +
            self.kuran_kulturune_uyum +
            self.hafta_basinda_kurs_zamanlamasi_giris +
            self.ders_saatlerinde_sinifa_zamanlama_giris_mutabaa_saatleri
        )
    
    def toplam_davranis_puani(self):
        """Toplam davranış puanını hesapla"""
        return (
            self.kultur_saatlari_ders_zamanlama_giris +
            self.sinif_hoca_ile_iletisim +
            self.arkadaslariyla_iletisim +
            self.namaz_vakitlerinde_mescide_zamanlama_giris +
            self.ibadet_disiplini +
            self.kilkiyafet_disiplini +
            self.yeme_icme_disiplini +
            self.yatalakhane_disiplini +
            self.trafic_kontrolu_kendini_cikisine_becerisi_temizlik_ve_duzen +
            self.genel_disiplin
        )
    
    def toplam_puan(self):
        """Toplam puanı hesapla"""
        return self.toplam_basari_puani() + self.toplam_davranis_puani()
    
    def __repr__(self):
        return f'<OgrenciPerformans {self.ogrenci_id} - {self.tarih}>'
