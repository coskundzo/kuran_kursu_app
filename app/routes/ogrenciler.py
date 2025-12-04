from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.ogrenci import Ogrenci
from app.models.egitmen import Egitmen
from app.models.kurs import Sinif
from datetime import datetime

bp = Blueprint('ogrenciler', __name__, url_prefix='/ogrenciler')


@bp.route('/')
@login_required
def liste():
    """Öğrenci listesi"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Kullanıcının kurs filtresi
    query = Ogrenci.query
    
    if current_user.tur == 3:  # Kurs kullanıcısı
        query = query.filter_by(kurs_id=current_user.kaynak_id)
    elif current_user.tur == 4:  # Eğitmen
        egitmen = Egitmen.query.get(current_user.kaynak_id)
        if egitmen:
            query = query.filter_by(kurs_id=egitmen.kurs_id)
    
    # Arama
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Ogrenci.adsoyad.like(f'%{search}%'),
                Ogrenci.tc.like(f'%{search}%'),
                Ogrenci.sicil_no.like(f'%{search}%')
            )
        )
    
    # Durum filtresi
    durum = request.args.get('durum', '')
    if durum:
        query = query.filter_by(durum=durum)
    
    # Sınıf filtresi
    sinif_id = request.args.get('sinif_id', type=int)
    if sinif_id:
        query = query.filter_by(sinif_id=sinif_id)
    
    # Sıralama
    order_by = request.args.get('order_by', 'adsoyad')
    if order_by == 'adsoyad':
        query = query.order_by(Ogrenci.adsoyad)
    elif order_by == 'kayit_tarihi':
        query = query.order_by(Ogrenci.kayit_tarihi.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    ogrenciler = pagination.items
    
    # Sınıf listesi (filtreleme için)
    siniflar = []
    if current_user.tur == 3:
        siniflar = Sinif.query.filter_by(kurs_id=current_user.kaynak_id).all()
    
    return render_template('ogrenciler/liste.html',
                         ogrenciler=ogrenciler,
                         pagination=pagination,
                         siniflar=siniflar,
                         search=search,
                         durum=durum)


@bp.route('/ekle', methods=['GET', 'POST'])
@login_required
def ekle():
    """Yeni öğrenci ekle"""
    if request.method == 'POST':
        try:
            # Kurs ID'sini belirle
            kurs_id = current_user.kaynak_id if current_user.tur == 3 else request.form.get('kurs_id', type=int)
            
            ogrenci = Ogrenci(
                adsoyad=request.form.get('adsoyad'),
                tc=request.form.get('tc'),
                dogum_tarihi=datetime.strptime(request.form.get('dogum_tarihi'), '%Y-%m-%d').date() if request.form.get('dogum_tarihi') else None,
                cinsiyet=request.form.get('cinsiyet'),
                telefon=request.form.get('telefon'),
                email=request.form.get('email'),
                adres=request.form.get('adres'),
                veli_adi=request.form.get('veli_adi'),
                veli_telefon=request.form.get('veli_telefon'),
                veli_email=request.form.get('veli_email'),
                kurs_id=kurs_id,
                sinif_id=request.form.get('sinif_id', type=int),
                egitmen_id=request.form.get('egitmen_id', type=int),
                sicil_no=request.form.get('sicil_no'),
                egitim_turu=request.form.get('egitim_turu'),
                durum='aktif'
            )
            
            db.session.add(ogrenci)
            db.session.commit()
            
            flash('Öğrenci başarıyla eklendi!', 'success')
            return redirect(url_for('ogrenciler.detay', id=ogrenci.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'danger')
    
    # Form için gerekli listeler
    siniflar = Sinif.query.filter_by(kurs_id=current_user.kaynak_id).all() if current_user.tur == 3 else []
    egitmenler = Egitmen.query.filter_by(kurs_id=current_user.kaynak_id).all() if current_user.tur == 3 else []
    
    return render_template('ogrenciler/form.html',
                         ogrenci=None,
                         siniflar=siniflar,
                         egitmenler=egitmenler)


@bp.route('/<int:id>')
@login_required
def detay(id):
    """Öğrenci detay sayfası"""
    ogrenci = Ogrenci.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and ogrenci.kurs_id != current_user.kaynak_id:
        flash('Bu öğrenciye erişim yetkiniz yok!', 'danger')
        return redirect(url_for('ogrenciler.liste'))
    
    return render_template('ogrenciler/detay.html', ogrenci=ogrenci)


@bp.route('/<int:id>/duzenle', methods=['GET', 'POST'])
@login_required
def duzenle(id):
    """Öğrenci düzenle"""
    ogrenci = Ogrenci.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and ogrenci.kurs_id != current_user.kaynak_id:
        flash('Bu öğrenciyi düzenleme yetkiniz yok!', 'danger')
        return redirect(url_for('ogrenciler.liste'))
    
    if request.method == 'POST':
        try:
            ogrenci.adsoyad = request.form.get('adsoyad')
            ogrenci.tc = request.form.get('tc')
            ogrenci.dogum_tarihi = datetime.strptime(request.form.get('dogum_tarihi'), '%Y-%m-%d').date() if request.form.get('dogum_tarihi') else None
            ogrenci.cinsiyet = request.form.get('cinsiyet')
            ogrenci.telefon = request.form.get('telefon')
            ogrenci.email = request.form.get('email')
            ogrenci.adres = request.form.get('adres')
            ogrenci.veli_adi = request.form.get('veli_adi')
            ogrenci.veli_telefon = request.form.get('veli_telefon')
            ogrenci.veli_email = request.form.get('veli_email')
            ogrenci.sinif_id = request.form.get('sinif_id', type=int)
            ogrenci.egitmen_id = request.form.get('egitmen_id', type=int)
            ogrenci.durum = request.form.get('durum')
            
            db.session.commit()
            
            flash('Öğrenci bilgileri güncellendi!', 'success')
            return redirect(url_for('ogrenciler.detay', id=ogrenci.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'danger')
    
    # Form için gerekli listeler
    siniflar = Sinif.query.filter_by(kurs_id=ogrenci.kurs_id).all()
    egitmenler = Egitmen.query.filter_by(kurs_id=ogrenci.kurs_id).all()
    
    return render_template('ogrenciler/form.html',
                         ogrenci=ogrenci,
                         siniflar=siniflar,
                         egitmenler=egitmenler)


@bp.route('/<int:id>/sil', methods=['POST'])
@login_required
def sil(id):
    """Öğrenci sil"""
    ogrenci = Ogrenci.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and ogrenci.kurs_id != current_user.kaynak_id:
        return jsonify({'success': False, 'message': 'Yetkiniz yok!'}), 403
    
    try:
        db.session.delete(ogrenci)
        db.session.commit()
        flash('Öğrenci silindi!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# API Endpoints
@bp.route('/api/<int:id>')
@login_required
def api_getir(id):
    """Öğrenci bilgilerini JSON olarak döndür"""
    ogrenci = Ogrenci.query.get_or_404(id)
    return jsonify(ogrenci.to_dict())
