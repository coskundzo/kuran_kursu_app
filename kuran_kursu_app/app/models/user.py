from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """Kullanıcı Modeli"""
    __tablename__ = 'kullanicilar'
    
    id = db.Column(db.Integer, primary_key=True)
    adsoyad = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    telefon = db.Column(db.String(20))
    
    # Kullanıcı türü: 1=Admin, 2=Müftü, 3=Kurs, 4=Eğitmen
    tur = db.Column(db.Integer, default=3, nullable=False)
    kaynak_id = db.Column(db.Integer)  # Kurs veya Eğitmen ID'si
    
    # Yetkiler (virgülle ayrılmış)
    yetkiler = db.Column(db.Text)
    
    # SMS Ayarları
    sms_user = db.Column(db.String(50))
    sms_pass = db.Column(db.String(50))
    sms_apikey = db.Column(db.String(100))
    sms_saglayici = db.Column(db.Integer, default=0)  # 0=ortak, 2=dakik, 7=netgsm vb.
    sms_title = db.Column(db.String(11))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    aktif = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        """Şifre hash'le"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Şifre kontrolü"""
        return check_password_hash(self.password_hash, password)
    
    def get_yetkiler(self):
        """Yetkileri liste olarak döndür"""
        if not self.yetkiler:
            return []
        return [y.strip() for y in self.yetkiler.split(',') if y.strip()]
    
    def has_yetki(self, yetki_kodu):
        """Kullanıcının belirli bir yetkisi var mı?"""
        if self.tur == 1:  # Admin
            return True
        if self.tur == 2 and yetki_kodu not in ['kurslar', 'muftu']:  # Müftü
            return True
        return yetki_kodu in self.get_yetkiler()
    
    def get_kurs_id(self):
        """Kullanıcının kurs ID'sini döndür"""
        if self.tur == 3:  # Kurs kullanıcısı
            return self.kaynak_id
        elif self.tur == 4:  # Eğitmen
            egitmen = Egitmen.query.get(self.kaynak_id)
            return egitmen.kurs_id if egitmen else None
        elif self.tur == 2:  # Müftü
            # Müftü'nün bağlı olduğu kursları getir
            from app.models.kurs import Kurs
            from app.models.muftuluk import Muftuluk
            
            muftu = Muftuluk.query.get(self.kaynak_id)
            if muftu:
                kurslar = Kurs.query.filter(
                    db.or_(
                        Kurs.muftu_id == muftu.id,
                        Kurs.muftu_id.in_(
                            db.select([Muftuluk.id]).where(Muftuluk.bag == muftu.id)
                        )
                    )
                ).all()
                return ','.join([str(k.id) for k in kurslar])
        return None
    
    def __repr__(self):
        return f'<User {self.email}>'
