# E-Kuran Kursu Yönetim Sistemi - Flask

Modern Flask teknolojisi ile geliştirilmiş Kuran kursları için kapsamlı yönetim sistemi.

## 🚀 Özellikler

### 📋 Temel Modüller
- **Öğrenci Yönetimi:** Öğrenci kayıt, takip, performans değerlendirme
- **Eğitmen Yönetimi:** Eğitmen kayıtları ve performans takibi
- **Ders Yönetimi:** Hafızlık dersleri, yüzüne dersler, özel dersler
- **Yoklama Sistemi:** Günlük yoklama ve devamsızlık takibi
- **Aidat Yönetimi:** Borç takibi ve ödeme yönetimi
- **SMS & Email:** Toplu bildirim gönderimi
- **Raporlama:** Detaylı analiz ve raporlar

### 🔐 Güvenlik
- Flask-Login ile kullanıcı doğrulama
- Bcrypt ile şifre hashleme
- CSRF koruması
- SQL Injection koruması (SQLAlchemy ORM)
- Role-based yetkilendirme (Admin, Müftü, Kurs, Eğitmen)

### 📱 Modern Arayüz
- Bootstrap 5 responsive tasarım
- Font Awesome ikonları
- AJAX ile dinamik işlemler
- Mobil uyumlu

## 🛠️ Teknoloji Stack

- **Backend:** Flask 3.0, Python 3.10+
- **Database:** MySQL 8.0 / MariaDB
- **ORM:** SQLAlchemy
- **Template Engine:** Jinja2
- **CSS Framework:** Bootstrap 5
- **Authentication:** Flask-Login
- **Migration:** Flask-Migrate
- **Email:** Flask-Mail
- **Task Queue:** Celery + Redis (opsiyonel)

## 📦 Kurulum

### 1. Gereksinimleri Yükleyin

```powershell
# Virtual environment oluştur
python -m venv venv

# Virtual environment'ı aktif et
.\venv\Scripts\Activate.ps1

# Paketleri yükle
pip install -r requirements.txt
```

### 2. Veritabanı Ayarları

`.env.example` dosyasını `.env` olarak kopyalayın ve düzenleyin:

```bash
cp .env.example .env
```

`.env` dosyasındaki veritabanı ayarlarını yapılandırın:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ekurs_db
DB_USER=root
DB_PASSWORD=your-password
SECRET_KEY=your-secret-key-change-this
```

### 3. Veritabanını Oluşturun

```powershell
# MySQL'e bağlan
mysql -u root -p

# Veritabanı oluştur
CREATE DATABASE ekurs_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

### 4. Migration İşlemleri

```powershell
# Migration klasörünü başlat
flask db init

# Migration oluştur
flask db migrate -m "Initial migration"

# Veritabanına uygula
flask db upgrade
```

### 5. İlk Admin Kullanıcısını Oluşturun

```powershell
# Python shell'i aç
flask shell

# Admin kullanıcısı oluştur
from app.models.user import User
from app import db

admin = User(
    email='admin@example.com',
    adsoyad='Admin User',
    tur=1,  # Admin
    aktif=True
)
admin.set_password('admin123')
db.session.add(admin)
db.session.commit()
exit()
```

### 6. Uygulamayı Çalıştırın

```powershell
# Development mode
flask run

# Veya
python run.py
```

Tarayıcıda açın: http://localhost:5000

**Giriş Bilgileri:**
- Email: admin@example.com
- Şifre: admin123

## 📁 Proje Yapısı

```
ekurs-flask/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # SQLAlchemy modelleri
│   │   ├── user.py          # Kullanıcı modeli
│   │   ├── ogrenci.py       # Öğrenci modeli
│   │   ├── egitmen.py       # Eğitmen modeli
│   │   ├── ders.py          # Ders modelleri
│   │   └── kurs.py          # Kurs modelleri
│   ├── routes/              # Blueprint route'lar
│   │   ├── auth.py          # Authentication
│   │   ├── main.py          # Ana sayfa
│   │   ├── ogrenciler.py    # Öğrenci işlemleri
│   │   ├── egitmenler.py    # Eğitmen işlemleri
│   │   ├── dersler.py       # Ders işlemleri
│   │   └── aidat.py         # Aidat işlemleri
│   ├── services/            # İş mantığı servisleri
│   │   ├── sms_service.py   # SMS gönderimi
│   │   ├── email_service.py # Email gönderimi
│   │   └── bildirim_service.py # Push bildirimleri
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html        # Ana template
│   │   ├── auth/            # Giriş sayfaları
│   │   ├── main/            # Dashboard
│   │   └── ogrenciler/      # Öğrenci sayfaları
│   ├── static/              # CSS, JS, resimler
│   │   ├── css/
│   │   ├── js/
│   │   └── uploads/
│   └── utils/               # Yardımcı fonksiyonlar
├── migrations/              # Alembic migrations
├── tests/                   # Test dosyaları
├── config.py               # Konfigürasyon
├── requirements.txt        # Python paketleri
├── .env.example           # Örnek environment variables
├── .gitignore
└── run.py                 # Uygulama başlatıcı
```

## 🔧 Yapılandırma

### SMS Ayarları

`.env` dosyasında SMS sağlayıcı ayarlarını yapın:

```env
SMS_PROVIDER=2              # 2=Dakik SMS, 7=NetGSM
SMS_USER=your-sms-username
SMS_PASSWORD=your-sms-password
SMS_TITLE=EKURANKURSU
```

### Email Ayarları

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Redis & Celery (Opsiyonel)

Arka plan işleri için:

```env
REDIS_URL=redis://localhost:6379/0
```

Celery worker başlat:

```powershell
celery -A app.celery worker --loglevel=info
```

## 📊 Kullanıcı Rolleri

1. **Admin (tur=1):** Tam yetki
2. **Müftü (tur=2):** Bağlı kursları yönetme
3. **Kurs (tur=3):** Kendi kursunu yönetme
4. **Eğitmen (tur=4):** Sınırlı erişim, öğrenci takibi

## 🧪 Test

```powershell
# Testleri çalıştır
pytest

# Coverage raporu
pytest --cov=app
```

## 📝 API Endpoints

### Öğrenci API
- `GET /ogrenciler/api/<id>` - Öğrenci bilgisi (JSON)
- `POST /ogrenciler/ekle` - Yeni öğrenci ekle
- `POST /ogrenciler/<id>/duzenle` - Öğrenci güncelle
- `POST /ogrenciler/<id>/sil` - Öğrenci sil

## 🚢 Production Deployment

### Gunicorn ile Çalıştırma

```powershell
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

### Nginx Konfigürasyonu

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/ekurs-flask/app/static;
    }
}
```

## 📚 Dokümantasyon

Detaylı dokümantasyon için: [Wiki sayfasına](../../wiki) bakın

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🆘 Destek

Sorularınız için:
- GitHub Issues: [Issues sayfası](../../issues)
- Email: info@example.com

## ✨ Özellik Roadmap

- [ ] Mobil uygulama API'leri
- [ ] Excel/PDF rapor export
- [ ] Çoklu dil desteği
- [ ] WebSocket ile real-time bildirimler
- [ ] Dashboard grafikler (Chart.js)
- [ ] QR kod ile yoklama
- [ ] Veli portal sistemi

---

**Geliştirici Notu:** Bu proje, eski PHP tabanlı E-Kuran Kursu sisteminin modern Flask ile yeniden yazılmış halidir.
