from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db
from app.models.ogrenci import Ogrenci
from app.models.egitmen import Egitmen
from app.models.ders import HafizlikDers, Yoklama
from datetime import datetime, timedelta
from sqlalchemy import func, and_

bp = Blueprint('main', __name__)


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    """Ana sayfa / Dashboard"""
    
    # Kullanıcının kurs ID'sini al
    kurs_filter = None
    if current_user.tur == 3:  # Kurs kullanıcısı
        kurs_filter = current_user.kaynak_id
    elif current_user.tur == 4:  # Eğitmen
        egitmen = Egitmen.query.get(current_user.kaynak_id)
        kurs_filter = egitmen.kurs_id if egitmen else None
    
    # İstatistikler
    stats = {}
    
    if kurs_filter:
        # Öğrenci sayısı
        stats['ogrenci_sayisi'] = Ogrenci.query.filter_by(
            kurs_id=kurs_filter,
            durum='aktif'
        ).count()
        
        # Eğitmen sayısı
        stats['egitmen_sayisi'] = Egitmen.query.filter_by(
            kurs_id=kurs_filter,
            durum='aktif'
        ).count()
        
        # Bugünkü yoklama bilgisi
        bugun = datetime.now().date()
        stats['bugun_gelen'] = Yoklama.query.join(Ogrenci).filter(
            and_(
                Yoklama.tarih == bugun,
                Yoklama.durum == 'geldi',
                Ogrenci.kurs_id == kurs_filter
            )
        ).count()
        
        stats['bugun_gelmeyen'] = Yoklama.query.join(Ogrenci).filter(
            and_(
                Yoklama.tarih == bugun,
                Yoklama.durum == 'gelmedi',
                Ogrenci.kurs_id == kurs_filter
            )
        ).count()
        
        # Bu ayki hafızlık dersleri
        ay_basi = datetime.now().replace(day=1).date()
        stats['aylik_ders'] = HafizlikDers.query.join(Ogrenci).filter(
            and_(
                HafizlikDers.tarih >= ay_basi,
                Ogrenci.kurs_id == kurs_filter
            )
        ).count()
    else:
        # Admin için genel istatistikler
        stats['ogrenci_sayisi'] = Ogrenci.query.filter_by(durum='aktif').count()
        stats['egitmen_sayisi'] = Egitmen.query.filter_by(durum='aktif').count()
        stats['bugun_gelen'] = 0
        stats['bugun_gelmeyen'] = 0
        stats['aylik_ders'] = 0
    
    # Son eklenen öğrenciler
    son_ogrenciler_query = Ogrenci.query.order_by(Ogrenci.created_at.desc()).limit(5)
    if kurs_filter:
        son_ogrenciler_query = son_ogrenciler_query.filter_by(kurs_id=kurs_filter)
    son_ogrenciler = son_ogrenciler_query.all()
    
    return render_template('main/index.html',
                         stats=stats,
                         son_ogrenciler=son_ogrenciler)


@bp.route('/profil')
@login_required
def profil():
    """Kullanıcı profili"""
    return render_template('main/profil.html')
