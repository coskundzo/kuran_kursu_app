from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.karne import KarneSablon, KarneSablonEleman
from app.models.kurs import Kurs
from app.models.ders import Ders
import os
from config import Config

bp = Blueprint('karneler', __name__, url_prefix='/karneler')

# İzin verilen dosya uzantıları
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/')
@login_required
def liste():
    """Karne şablonları listesi"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = KarneSablon.query
    
    # Kurs yöneticisi ise sadece kendi kursunun şablonlarını görsün
    if current_user.tur == 3:
        query = query.filter_by(kurs_id=current_user.kaynak_id)
    
    # Arama
    search = request.args.get('search', '')
    if search:
        query = query.filter(KarneSablon.adi.like(f'%{search}%'))
    
    # Sıralama
    query = query.order_by(KarneSablon.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    sablonlar = pagination.items
    
    return render_template('karneler/liste.html',
                         sablonlar=sablonlar,
                         pagination=pagination,
                         search=search)


@bp.route('/yeni', methods=['GET', 'POST'])
@login_required
def yeni():
    """Yeni karne şablonu oluştur"""
    if request.method == 'POST':
        try:
            # Kurs ID kontrolü
            kurs_id = request.form.get('kurs_id', type=int)
            if current_user.tur == 3:
                kurs_id = current_user.kaynak_id
            
            # Arkaplan dosyası yükleme
            arkaplan_path = None
            if 'arkaplan' in request.files:
                file = request.files['arkaplan']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Benzersiz dosya adı oluştur
                    from datetime import datetime
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"karne_{timestamp}_{filename}"
                    
                    upload_folder = os.path.join(Config.UPLOAD_FOLDER, 'karneler')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    arkaplan_path = f'karneler/{filename}'
            
            sablon = KarneSablon(
                adi=request.form.get('adi'),
                kurs_id=kurs_id,
                arkaplan=arkaplan_path,
                genislik=request.form.get('genislik', 800, type=int),
                yukseklik=request.form.get('yukseklik', 1131, type=int)
            )
            
            db.session.add(sablon)
            db.session.commit()
            
            flash('Karne şablonu başarıyla oluşturuldu!', 'success')
            return redirect(url_for('karneler.duzenle', id=sablon.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hata: {str(e)}', 'danger')
    
    # Form için gerekli veriler
    if current_user.tur == 3:
        kurslar = Kurs.query.filter_by(id=current_user.kaynak_id, aktif=True).all()
    else:
        kurslar = Kurs.query.filter_by(aktif=True).all()
    
    return render_template('karneler/form.html', kurslar=kurslar)


@bp.route('/<int:id>/duzenle', methods=['GET', 'POST'])
@login_required
def duzenle(id):
    """Karne şablonu düzenle"""
    sablon = KarneSablon.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and sablon.kurs_id != current_user.kaynak_id:
        flash('Bu şablonu düzenleme yetkiniz yok!', 'danger')
        return redirect(url_for('karneler.liste'))
    
    if request.method == 'POST':
        try:
            sablon.adi = request.form.get('adi')
            sablon.genislik = request.form.get('genislik', 800, type=int)
            sablon.yukseklik = request.form.get('yukseklik', 1131, type=int)
            
            # Yeni arkaplan dosyası yükleme
            if 'arkaplan' in request.files:
                file = request.files['arkaplan']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    from datetime import datetime
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"karne_{timestamp}_{filename}"
                    
                    upload_folder = os.path.join(Config.UPLOAD_FOLDER, 'karneler')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    sablon.arkaplan = f'karneler/{filename}'
            
            db.session.commit()
            flash('Karne şablonu güncellendi!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hata: {str(e)}', 'danger')
    
    # Kullanılabilir değişkenler
    degiskenler = [
        {'kod': 'ogrenci.adsoyad', 'ad': 'Öğrenci Ad Soyad'},
        {'kod': 'ogrenci.tc', 'ad': 'TC Kimlik No'},
        {'kod': 'ogrenci.telefon', 'ad': 'Telefon'},
        {'kod': 'ogrenci.dogum_tarihi', 'ad': 'Doğum Tarihi'},
        {'kod': 'sinif.adi', 'ad': 'Sınıf Adı'},
        {'kod': 'sinif.seviye', 'ad': 'Seviye'},
        {'kod': 'kurs.adi', 'ad': 'Kurs Adı'},
        {'kod': 'egitmen.adsoyad', 'ad': 'Eğitmen Ad Soyad'},
        {'kod': 'donem', 'ad': 'Dönem'},
        {'kod': 'tarih', 'ad': 'Tarih'},
    ]
    
    # Dersler
    if sablon.kurs_id:
        dersler = Ders.query.filter_by(kurs_id=sablon.kurs_id).all()
    else:
        dersler = Ders.query.all()
    
    # Şablon elemanları
    elemanlar = sablon.elemanlar.order_by(KarneSablonEleman.sira).all()
    
    return render_template('karneler/duzenle.html',
                         sablon=sablon,
                         degiskenler=degiskenler,
                         dersler=dersler,
                         elemanlar=elemanlar)


@bp.route('/<int:id>/eleman-ekle', methods=['POST'])
@login_required
def eleman_ekle(id):
    """Şablona yeni eleman ekle"""
    sablon = KarneSablon.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and sablon.kurs_id != current_user.kaynak_id:
        return jsonify({'success': False, 'message': 'Yetkiniz yok!'}), 403
    
    try:
        data = request.json
        
        eleman = KarneSablonEleman(
            sablon_id=sablon.id,
            tip=data.get('tip'),
            anahtar=data.get('anahtar'),
            metin=data.get('metin'),
            x=data.get('x', 0),
            y=data.get('y', 0),
            font_boyut=data.get('font_boyut', 14),
            font_renk=data.get('font_renk', '#000000'),
            font_stili=data.get('font_stili', 'normal'),
            hizalama=data.get('hizalama', 'left'),
            genislik=data.get('genislik', 200),
            sira=sablon.elemanlar.count()
        )
        
        db.session.add(eleman)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'eleman': {
                'id': eleman.id,
                'tip': eleman.tip,
                'anahtar': eleman.anahtar,
                'metin': eleman.metin,
                'x': eleman.x,
                'y': eleman.y,
                'font_boyut': eleman.font_boyut,
                'font_renk': eleman.font_renk,
                'font_stili': eleman.font_stili,
                'hizalama': eleman.hizalama,
                'genislik': eleman.genislik
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/eleman/<int:id>/guncelle', methods=['POST'])
@login_required
def eleman_guncelle(id):
    """Elemanı güncelle"""
    eleman = KarneSablonEleman.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and eleman.sablon.kurs_id != current_user.kaynak_id:
        return jsonify({'success': False, 'message': 'Yetkiniz yok!'}), 403
    
    try:
        data = request.json
        
        eleman.x = data.get('x', eleman.x)
        eleman.y = data.get('y', eleman.y)
        eleman.font_boyut = data.get('font_boyut', eleman.font_boyut)
        eleman.font_renk = data.get('font_renk', eleman.font_renk)
        eleman.font_stili = data.get('font_stili', eleman.font_stili)
        eleman.hizalama = data.get('hizalama', eleman.hizalama)
        eleman.genislik = data.get('genislik', eleman.genislik)
        eleman.metin = data.get('metin', eleman.metin)
        
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/eleman/<int:id>/sil', methods=['POST'])
@login_required
def eleman_sil(id):
    """Elemanı sil"""
    eleman = KarneSablonEleman.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and eleman.sablon.kurs_id != current_user.kaynak_id:
        return jsonify({'success': False, 'message': 'Yetkiniz yok!'}), 403
    
    try:
        db.session.delete(eleman)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/<int:id>/sil', methods=['POST'])
@login_required
def sil(id):
    """Karne şablonu sil"""
    sablon = KarneSablon.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and sablon.kurs_id != current_user.kaynak_id:
        flash('Bu şablonu silme yetkiniz yok!', 'danger')
        return redirect(url_for('karneler.liste'))
    
    try:
        sablon_adi = sablon.adi
        db.session.delete(sablon)
        db.session.commit()
        
        flash(f'{sablon_adi} şablonu başarıyla silindi!', 'success')
        return redirect(url_for('karneler.liste'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Hata: {str(e)}', 'danger')
        return redirect(url_for('karneler.liste'))
