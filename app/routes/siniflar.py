from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.sinif import Sinif
from app.models.kurs import Kurs
from app.models.egitmen import Egitmen

bp = Blueprint('siniflar', __name__, url_prefix='/siniflar')


@bp.route('/')
@login_required
def liste():
    """Sınıf listesi"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = Sinif.query
    
    # Kurs yöneticisi ise sadece kendi kursunun sınıflarını görsün
    if current_user.tur == 3:
        query = query.filter_by(kurs_id=current_user.kaynak_id)
    
    # Arama
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Sinif.adi.like(f'%{search}%'),
                Sinif.kod.like(f'%{search}%')
            )
        )
    
    # Durum filtresi
    durum = request.args.get('durum', '')
    if durum == 'aktif':
        query = query.filter_by(aktif=True)
    elif durum == 'pasif':
        query = query.filter_by(aktif=False)
    
    # Tür filtresi
    tur = request.args.get('tur', '')
    if tur:
        query = query.filter_by(tur=tur)
    
    # Sıralama
    query = query.order_by(Sinif.adi.asc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    siniflar = pagination.items
    
    return render_template('siniflar/liste.html',
                         siniflar=siniflar,
                         pagination=pagination,
                         search=search,
                         durum=durum,
                         tur=tur)


@bp.route('/ekle', methods=['GET', 'POST'])
@login_required
def ekle():
    """Yeni sınıf ekle"""
    if request.method == 'POST':
        try:
            # Kurs ID kontrolü
            kurs_id = request.form.get('kurs_id', type=int)
            if current_user.tur == 3:
                kurs_id = current_user.kaynak_id
            
            sinif = Sinif(
                adi=request.form.get('adi'),
                kod=request.form.get('kod'),
                kurs_id=kurs_id,
                egitmen_id=request.form.get('egitmen_id', type=int) or None,
                seviye=request.form.get('seviye'),
                tur=request.form.get('tur'),
                kontenjan=request.form.get('kontenjan', type=int),
                ders_gunleri=request.form.get('ders_gunleri'),
                ders_saati=request.form.get('ders_saati'),
                aciklama=request.form.get('aciklama'),
                aktif=True
            )
            
            db.session.add(sinif)
            db.session.commit()
            
            flash('Sınıf başarıyla eklendi!', 'success')
            return redirect(url_for('siniflar.detay', id=sinif.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hata: {str(e)}', 'danger')
    
    # Form için gerekli veriler
    if current_user.tur == 3:
        kurslar = Kurs.query.filter_by(id=current_user.kaynak_id, aktif=True).all()
        egitmenler = Egitmen.query.filter_by(kurs_id=current_user.kaynak_id, durum='aktif').all()
    else:
        kurslar = Kurs.query.filter_by(aktif=True).all()
        egitmenler = Egitmen.query.filter_by(durum='aktif').all()
    
    return render_template('siniflar/form.html',
                         kurslar=kurslar,
                         egitmenler=egitmenler)


@bp.route('/<int:id>')
@login_required
def detay(id):
    """Sınıf detay sayfası"""
    sinif = Sinif.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and sinif.kurs_id != current_user.kaynak_id:
        flash('Bu sınıfa erişim yetkiniz yok!', 'danger')
        return redirect(url_for('siniflar.liste'))
    
    # Sınıf öğrencileri
    ogrenciler = sinif.ogrenciler.filter_by(durum='aktif').all()
    
    return render_template('siniflar/detay.html',
                         sinif=sinif,
                         ogrenciler=ogrenciler)


@bp.route('/<int:id>/duzenle', methods=['GET', 'POST'])
@login_required
def duzenle(id):
    """Sınıf düzenle"""
    sinif = Sinif.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and sinif.kurs_id != current_user.kaynak_id:
        flash('Bu sınıfı düzenleme yetkiniz yok!', 'danger')
        return redirect(url_for('siniflar.liste'))
    
    if request.method == 'POST':
        try:
            sinif.adi = request.form.get('adi')
            sinif.kod = request.form.get('kod')
            sinif.egitmen_id = request.form.get('egitmen_id', type=int) or None
            sinif.seviye = request.form.get('seviye')
            sinif.tur = request.form.get('tur')
            sinif.kontenjan = request.form.get('kontenjan', type=int)
            sinif.ders_gunleri = request.form.get('ders_gunleri')
            sinif.ders_saati = request.form.get('ders_saati')
            sinif.aciklama = request.form.get('aciklama')
            
            # Aktiflik durumu
            aktif = request.form.get('aktif')
            sinif.aktif = aktif == '1' or aktif == 'on'
            
            db.session.commit()
            flash('Sınıf bilgileri güncellendi!', 'success')
            return redirect(url_for('siniflar.detay', id=sinif.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hata: {str(e)}', 'danger')
    
    # Form için gerekli veriler
    if current_user.tur == 3:
        kurslar = Kurs.query.filter_by(id=current_user.kaynak_id, aktif=True).all()
        egitmenler = Egitmen.query.filter_by(kurs_id=current_user.kaynak_id, durum='aktif').all()
    else:
        kurslar = Kurs.query.filter_by(aktif=True).all()
        egitmenler = Egitmen.query.filter_by(durum='aktif').all()
    
    return render_template('siniflar/form.html',
                         sinif=sinif,
                         kurslar=kurslar,
                         egitmenler=egitmenler)


@bp.route('/<int:id>/sil', methods=['POST'])
@login_required
def sil(id):
    """Sınıf sil (hard delete)"""
    sinif = Sinif.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and sinif.kurs_id != current_user.kaynak_id:
        flash('Bu sınıfı silme yetkiniz yok!', 'danger')
        return redirect(url_for('siniflar.liste'))
    
    # Eğer sınıfta öğrenci varsa silme
    if sinif.mevcud_ogrenci_sayisi > 0:
        flash('Sınıfta aktif öğrenci bulunduğu için silinemez!', 'danger')
        return redirect(url_for('siniflar.liste'))
    
    try:
        sinif_adi = sinif.adi
        db.session.delete(sinif)
        db.session.commit()
        
        flash(f'{sinif_adi} sınıfı başarıyla silindi!', 'success')
        return redirect(url_for('siniflar.liste'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Hata: {str(e)}', 'danger')
        return redirect(url_for('siniflar.liste'))


@bp.route('/api/siniflar/<int:kurs_id>')
@login_required
def api_siniflar(kurs_id):
    """Kursa göre sınıfları getir (AJAX için)"""
    siniflar = Sinif.query.filter_by(kurs_id=kurs_id, aktif=True).all()
    return jsonify([{
        'id': s.id,
        'adi': s.adi,
        'bos_kontenjan': s.bos_kontenjan
    } for s in siniflar])
