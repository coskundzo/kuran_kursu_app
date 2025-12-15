"""Veritabanına örnek veri ekleyen script"""
from app import create_app, db
from app.models.kurs import Kurs, Sinif
from app.models.egitmen import Egitmen
from app.models.ogrenci import Ogrenci
from app.models.ders import Ders
from datetime import date, datetime, time

def seed_data():
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("VERİ EKLEME İŞLEMİ BAŞLIYOR")
        print("=" * 60)
        
        # 1. KURS EKLE
        print("\n📚 KURSLAR:")
        kurslar_data = [
            {
                "adi": "Merkez Kuran Kursu",
                "kod": "MRK001",
                "adres": "Atatürk Mah. Cumhuriyet Cad. No:45 Merkez",
                "telefon": "0312 123 4567",
                "email": "merkez@kurankursu.com"
            },
            {
                "adi": "Yeni Mahalle Kuran Kursu",
                "kod": "YM002",
                "adres": "Yeni Mah. İstiklal Sok. No:12",
                "telefon": "0312 234 5678",
                "email": "yenimahalle@kurankursu.com"
            }
        ]
        
        kurs_ids = []
        for kurs_data in kurslar_data:
            existing = Kurs.query.filter_by(kod=kurs_data["kod"]).first()
            if not existing:
                kurs = Kurs(
                    adi=kurs_data["adi"],
                    kod=kurs_data["kod"],
                    adres=kurs_data["adres"],
                    telefon=kurs_data["telefon"],
                    email=kurs_data["email"],
                    aktif=True
                )
                db.session.add(kurs)
                db.session.flush()
                kurs_ids.append(kurs.id)
                print(f"  ✓ Kurs eklendi: {kurs_data['adi']}")
            else:
                kurs_ids.append(existing.id)
                print(f"  ⊘ Kurs zaten var: {kurs_data['adi']}")
        
        db.session.commit()
        
        # 2. SINIF EKLE
        print("\n🎓 SINIFLAR:")
        kurs = Kurs.query.first()
        if not kurs:
            print("  ❌ Kurs bulunamadı!")
            return
            
        siniflar_data = [
            {"adi": "Hafızlık 1. Sınıf", "kapasite": 20},
            {"adi": "Hafızlık 2. Sınıf", "kapasite": 20},
            {"adi": "Hafızlık 3. Sınıf", "kapasite": 20},
            {"adi": "Temel Kur'an 1", "kapasite": 25},
            {"adi": "Temel Kur'an 2", "kapasite": 25},
            {"adi": "İleri Seviye", "kapasite": 15},
        ]
        
        sinif_ids = []
        for sinif_data in siniflar_data:
            existing = Sinif.query.filter_by(adi=sinif_data["adi"], kurs_id=kurs.id).first()
            if not existing:
                sinif = Sinif(
                    adi=sinif_data["adi"],
                    kurs_id=kurs.id,
                    kapasite=sinif_data["kapasite"],
                    aktif=True
                )
                db.session.add(sinif)
                db.session.flush()
                sinif_ids.append(sinif.id)
                print(f"  ✓ Sınıf eklendi: {sinif_data['adi']}")
            else:
                sinif_ids.append(existing.id)
                print(f"  ⊘ Sınıf zaten var: {sinif_data['adi']}")
        
        db.session.commit()
        
        # 3. EĞİTMEN EKLE
        print("\n👨‍🏫 EĞİTMENLER:")
        egitmenler_data = [
            {
                "adsoyad": "Ahmet Yılmaz",
                "tc": "12345678901",
                "telefon": "0555 111 2233",
                "email": "ahmet.yilmaz@example.com",
                "brans": "Hafızlık",
                "cinsiyet": "E",
                "dogum_tarihi": date(1985, 3, 15)
            },
            {
                "adsoyad": "Ayşe Demir",
                "tc": "98765432109",
                "telefon": "0555 444 5566",
                "email": "ayse.demir@example.com",
                "brans": "Temel Kur'an",
                "cinsiyet": "K",
                "dogum_tarihi": date(1990, 7, 20)
            },
            {
                "adsoyad": "Mehmet Kaya",
                "tc": "11223344556",
                "telefon": "0555 777 8899",
                "email": "mehmet.kaya@example.com",
                "brans": "Tecvid",
                "cinsiyet": "E",
                "dogum_tarihi": date(1988, 11, 5)
            },
            {
                "adsoyad": "Fatma Şahin",
                "tc": "55667788990",
                "telefon": "0555 222 3344",
                "email": "fatma.sahin@example.com",
                "brans": "Meal-Tefsir",
                "cinsiyet": "K",
                "dogum_tarihi": date(1992, 4, 12)
            }
        ]
        
        egitmen_ids = []
        for egitmen_data in egitmenler_data:
            existing = Egitmen.query.filter_by(tc=egitmen_data["tc"]).first()
            if not existing:
                egitmen = Egitmen(
                    adsoyad=egitmen_data["adsoyad"],
                    tc=egitmen_data["tc"],
                    telefon=egitmen_data["telefon"],
                    email=egitmen_data["email"],
                    brans=egitmen_data["brans"],
                    cinsiyet=egitmen_data["cinsiyet"],
                    dogum_tarihi=egitmen_data["dogum_tarihi"],
                    kurs_id=kurs.id,
                    durum='aktif',
                    baslangic_tarihi=date(2024, 9, 1)
                )
                db.session.add(egitmen)
                db.session.flush()
                egitmen_ids.append(egitmen.id)
                print(f"  ✓ Eğitmen eklendi: {egitmen_data['adsoyad']}")
            else:
                egitmen_ids.append(existing.id)
                print(f"  ⊘ Eğitmen zaten var: {egitmen_data['adsoyad']}")
        
        db.session.commit()
        
        # 4. ÖĞRENCİ EKLE
        print("\n👦 ÖĞRENCİLER:")
        ogrenciler_data = [
            {
                "adsoyad": "Ali Veli Yıldız",
                "tc": "12312312312",
                "dogum_tarihi": date(2010, 5, 20),
                "cinsiyet": "E",
                "telefon": "0533 111 2222",
                "email": "ali.yildiz@example.com",
                "veli_adi": "Hasan Yıldız",
                "veli_telefon": "0532 222 3333",
                "sicil_no": "2024001",
                "egitim_turu": "Hafızlık"
            },
            {
                "adsoyad": "Zeynep Ak",
                "tc": "32132132132",
                "dogum_tarihi": date(2012, 8, 15),
                "cinsiyet": "K",
                "telefon": "0533 444 5555",
                "email": "zeynep.ak@example.com",
                "veli_adi": "Ayşe Ak",
                "veli_telefon": "0532 555 6666",
                "sicil_no": "2024002",
                "egitim_turu": "Temel Kur'an"
            },
            {
                "adsoyad": "Mehmet Can Öz",
                "tc": "45645645645",
                "dogum_tarihi": date(2011, 3, 10),
                "cinsiyet": "E",
                "telefon": "0533 777 8888",
                "veli_adi": "Ahmet Öz",
                "veli_telefon": "0532 888 9999",
                "sicil_no": "2024003",
                "egitim_turu": "Hafızlık"
            },
            {
                "adsoyad": "Elif Yılmaz",
                "tc": "78978978978",
                "dogum_tarihi": date(2013, 12, 5),
                "cinsiyet": "K",
                "telefon": "0533 333 4444",
                "veli_adi": "Fatma Yılmaz",
                "veli_telefon": "0532 444 5555",
                "sicil_no": "2024004",
                "egitim_turu": "Temel Kur'an"
            },
            {
                "adsoyad": "Ahmet Kara",
                "tc": "15915915915",
                "dogum_tarihi": date(2009, 6, 25),
                "cinsiyet": "E",
                "telefon": "0533 666 7777",
                "veli_adi": "Mehmet Kara",
                "veli_telefon": "0532 777 8888",
                "sicil_no": "2024005",
                "egitim_turu": "Hafızlık"
            }
        ]
        
        for i, ogrenci_data in enumerate(ogrenciler_data):
            existing = Ogrenci.query.filter_by(tc=ogrenci_data["tc"]).first()
            if not existing:
                ogrenci = Ogrenci(
                    adsoyad=ogrenci_data["adsoyad"],
                    tc=ogrenci_data["tc"],
                    dogum_tarihi=ogrenci_data["dogum_tarihi"],
                    cinsiyet=ogrenci_data["cinsiyet"],
                    telefon=ogrenci_data.get("telefon"),
                    email=ogrenci_data.get("email"),
                    veli_adi=ogrenci_data["veli_adi"],
                    veli_telefon=ogrenci_data["veli_telefon"],
                    kurs_id=kurs.id,
                    sinif_id=sinif_ids[i % len(sinif_ids)] if sinif_ids else None,
                    egitmen_id=egitmen_ids[i % len(egitmen_ids)] if egitmen_ids else None,
                    sicil_no=ogrenci_data["sicil_no"],
                    egitim_turu=ogrenci_data["egitim_turu"],
                    kayit_tarihi=date(2024, 9, 1),
                    durum='aktif'
                )
                db.session.add(ogrenci)
                print(f"  ✓ Öğrenci eklendi: {ogrenci_data['adsoyad']}")
            else:
                print(f"  ⊘ Öğrenci zaten var: {ogrenci_data['adsoyad']}")
        
        db.session.commit()
        
        # 5. DERS EKLE
        print("\n📖 DERSLER:")
        if egitmen_ids and sinif_ids:
            dersler_data = [
                {
                    "adi": "Hafızlık Dersi - Sabah",
                    "tur": "Hafızlık",
                    "tarih": date(2024, 12, 9),
                    "baslangic_saati": time(9, 0),
                    "bitis_saati": time(11, 0)
                },
                {
                    "adi": "Temel Kur'an - Öğleden Sonra",
                    "tur": "Temel Kur'an",
                    "tarih": date(2024, 12, 10),
                    "baslangic_saati": time(14, 0),
                    "bitis_saati": time(15, 30)
                },
                {
                    "adi": "Tecvid Dersi",
                    "tur": "Tecvid",
                    "tarih": date(2024, 12, 11),
                    "baslangic_saati": time(10, 0),
                    "bitis_saati": time(11, 0)
                },
                {
                    "adi": "Meal-Tefsir",
                    "tur": "Meal",
                    "tarih": date(2024, 12, 12),
                    "baslangic_saati": time(15, 0),
                    "bitis_saati": time(16, 30)
                }
            ]
            
            for i, ders_data in enumerate(dersler_data):
                existing = Ders.query.filter_by(
                    adi=ders_data["adi"],
                    kurs_id=kurs.id
                ).first()
                if not existing:
                    ders = Ders(
                        adi=ders_data["adi"],
                        tur=ders_data["tur"],
                        tarih=ders_data["tarih"],
                        baslangic_saati=ders_data["baslangic_saati"],
                        bitis_saati=ders_data["bitis_saati"],
                        kurs_id=kurs.id,
                        egitmen_id=egitmen_ids[i % len(egitmen_ids)],
                        sinif_id=sinif_ids[i % len(sinif_ids)]
                    )
                    db.session.add(ders)
                    print(f"  ✓ Ders eklendi: {ders_data['adi']}")
                else:
                    print(f"  ⊘ Ders zaten var: {ders_data['adi']}")
            
            db.session.commit()
        
        # ÖZET
        print("\n" + "=" * 60)
        print("✅ TÜM VERİLER BAŞARIYLA EKLENDİ!")
        print("=" * 60)
        print(f"   📚 Toplam Kurs     : {Kurs.query.count()}")
        print(f"   🎓 Toplam Sınıf    : {Sinif.query.count()}")
        print(f"   👨‍🏫 Toplam Eğitmen  : {Egitmen.query.count()}")
        print(f"   👦 Toplam Öğrenci  : {Ogrenci.query.count()}")
        print(f"   📖 Toplam Ders     : {Ders.query.count()}")
        print("=" * 60)

if __name__ == '__main__':
    seed_data()
