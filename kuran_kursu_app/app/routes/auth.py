from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.forms import LoginForm
from flask_login import login_user, logout_user, current_user
from app import db
from app.models.user import User

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Giriş sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.aktif:
                flash('Hesabınız aktif değil. Lütfen yönetici ile iletişime geçin.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('E-posta veya şifre hatalı!', 'danger')
    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    """Çıkış işlemi"""
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Kayıt sayfası (opsiyonel)"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        adsoyad = request.form.get('adsoyad')
        
        # Kullanıcı var mı kontrol et
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Bu e-posta adresi zaten kayıtlı!', 'danger')
            return redirect(url_for('auth.register'))
        
        # Yeni kullanıcı oluştur
        user = User(
            email=email,
            adsoyad=adsoyad,
            tur=3,  # Varsayılan olarak kurs kullanıcısı
            aktif=False  # Admin onayı gerekiyor
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Kayıt başarılı! Hesabınız yönetici onayı bekliyor.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')
