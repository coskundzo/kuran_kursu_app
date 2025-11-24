from app import create_app, db
from app.models.user import User

app = create_app('development')

with app.app_context():
    # Önce admin kullanıcısı var mı kontrol et
    admin = User.query.filter_by(email='admin@ekurs.com').first()
    
    if admin:
        print(f"Admin kullanıcı zaten var: {admin.email}")
    else:
        # Yeni admin kullanıcısı oluştur
        admin = User(
            adsoyad='Admin',
            email='admin@ekurs.com',
            telefon='5555555555',
            tur=1,  # Admin
            aktif=True
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"✓ Admin kullanıcı oluşturuldu:")
        print(f"  Email: {admin.email}")
        print(f"  Şifre: admin123")
        print(f"  Tür: Admin (1)")
    
    # Test kullanıcısı ekle
    test_user = User.query.filter_by(email='test@ekurs.com').first()
    
    if test_user:
        print(f"\nTest kullanıcı zaten var: {test_user.email}")
    else:
        test_user = User(
            adsoyad='Test Kullanıcı',
            email='test@ekurs.com',
            telefon='5551234567',
            tur=3,  # Kurs kullanıcısı
            aktif=True
        )
        test_user.set_password('test123')
        
        db.session.add(test_user)
        db.session.commit()
        
        print(f"\n✓ Test kullanıcı oluşturuldu:")
        print(f"  Email: {test_user.email}")
        print(f"  Şifre: test123")
        print(f"  Tür: Kurs (3)")
