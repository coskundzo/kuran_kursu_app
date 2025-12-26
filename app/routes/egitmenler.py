

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.egitmen import Egitmen
from app.models.kurs import Kurs
from app.models.egitmen_performans import EgitmenPerformans
from app.forms import EgitmenForm
from datetime import datetime

bp = Blueprint('egitmenler', __name__, url_prefix='/egitmenler')

@bp.route('/')
@login_required
def liste():
    egitmenler = Egitmen.query.all()
    return render_template('egitmenler/liste.html', egitmenler=egitmenler)

@bp.route('/performans-liste')
@login_required
def performans_liste():
    """Eğitmen performans değerlendirmeleri listesi"""
    # Kullanıcı yetkisine göre eğitmenleri filtrele
    if current_user.tur == 3:  # Kurs yöneticisi
        egitmenler = Egitmen.query.filter_by(
            kurs_id=current_user.kaynak_id,
            durum='aktif'
        ).order_by(Egitmen.adsoyad).all()
    else:  # Admin veya diğer yetkiler
        egitmenler = Egitmen.query.filter_by(durum='aktif').order_by(Egitmen.adsoyad).all()
    
    # Her eğitmen için son performans kaydını al
    egitmen_performans_list = []
    for egitmen in egitmenler:
        son_performans = EgitmenPerformans.query.filter_by(
            egitmen_id=egitmen.id
        ).order_by(EgitmenPerformans.yil.desc(), EgitmenPerformans.ay.desc()).first()
        
        egitmen_performans_list.append({
            'egitmen': egitmen,
            'son_yil': son_performans.yil if son_performans else None,
            'son_ay': son_performans.ay if son_performans else None
        })
    
    return render_template('egitmenler/performans_liste.html', 
                         egitmen_performans_list=egitmen_performans_list)

@bp.route('/ekle', methods=['GET', 'POST'])
@login_required
def ekle():
    form = EgitmenForm()
    # Kurs seçeneklerini yükle
    form.kurs_id.choices = [(k.id, k.adi) for k in Kurs.query.filter_by(aktif=True).all()]
    
    if form.validate_on_submit():
        egitmen = Egitmen(
            adsoyad=form.adsoyad.data,
            tc=form.tc.data,
            telefon=form.telefon.data,
            email=form.email.data,
            brans=form.brans.data,
            kurs_id=form.kurs_id.data,
            durum='aktif'
        )
        db.session.add(egitmen)
        db.session.commit()
        flash('Eğitmen başarıyla eklendi!', 'success')
        return redirect(url_for('egitmenler.liste'))
    return render_template('egitmenler/form.html', form=form)

@bp.route('/<int:id>')
@login_required
def detay(id):
    """Eğitmen detay sayfası"""
    egitmen = Egitmen.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and egitmen.kurs_id != current_user.kaynak_id:
        flash('Bu eğitmene erişim yetkiniz yok!', 'danger')
        return redirect(url_for('egitmenler.liste'))
    
    return render_template('egitmenler/detay.html', egitmen=egitmen)

@bp.route('/<int:id>/duzenle', methods=['GET', 'POST'])
@login_required
def duzenle(id):
    """Eğitmen düzenle"""
    egitmen = Egitmen.query.get_or_404(id)
    form = EgitmenForm(obj=egitmen)
    
    # Yetki kontrolü
    if current_user.tur == 3 and egitmen.kurs_id != current_user.kaynak_id:
        flash('Bu eğitmeni düzenleme yetkiniz yok!', 'danger')
        return redirect(url_for('egitmenler.liste'))
    
    # Kurs seçeneklerini yükle
    form.kurs_id.choices = [(k.id, k.adi) for k in Kurs.query.filter_by(aktif=True).all()]
    
    if form.validate_on_submit():
        egitmen.adsoyad = form.adsoyad.data
        egitmen.tc = form.tc.data
        egitmen.telefon = form.telefon.data
        egitmen.email = form.email.data
        egitmen.brans = form.brans.data
        egitmen.kurs_id = form.kurs_id.data
        
        db.session.commit()
        flash('Eğitmen bilgileri güncellendi!', 'success')
        return redirect(url_for('egitmenler.detay', id=egitmen.id))
    
    return render_template('egitmenler/form.html', form=form, egitmen=egitmen)


@bp.route('/<int:id>/performans')
@login_required
def performans(id):
    """Eğitmen performans değerlendirme sayfası"""
    from datetime import datetime
    
    egitmen = Egitmen.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and egitmen.kurs_id != current_user.kaynak_id:
        flash('Bu eğitmenin performansına erişim yetkiniz yok!', 'danger')
        return redirect(url_for('egitmenler.liste'))
    
    # Yıl ve ay parametreleri
    yil = request.args.get('yil', datetime.now().year, type=int)
    ay = request.args.get('ay', datetime.now().month, type=int)
    
    # Mevcut performans verilerini al
    performanslar = EgitmenPerformans.query.filter_by(
        egitmen_id=id,
        yil=yil,
        ay=ay
    ).all()
    
    return render_template('egitmenler/performans.html', 
                         egitmen=egitmen, 
                         yil=yil, 
                         ay=ay,
                         performanslar=performanslar)


@bp.route('/<int:id>/performans/kaydet', methods=['POST'])
@login_required
def performans_kaydet(id):
    """Eğitmen performans verilerini kaydet"""
    try:
        egitmen = Egitmen.query.get_or_404(id)
        
        # Yetki kontrolü
        if current_user.tur == 3 and egitmen.kurs_id != current_user.kaynak_id:
            return jsonify({
                'success': False,
                'message': 'Bu eğitmenin performansını güncelleme yetkiniz yok!'
            }), 403
        
        data = request.get_json()
        yil = data.get('yil')
        ay = data.get('ay')
        kriterler = data.get('kriterler', [])
        
        # Bu ay için mevcut kayıtları sil
        EgitmenPerformans.query.filter_by(
            egitmen_id=id,
            yil=yil,
            ay=ay
        ).delete()
        
        # Yeni kayıtları ekle
        for kriter in kriterler:
            performans = EgitmenPerformans(
                egitmen_id=id,
                yil=yil,
                ay=ay,
                kriter=kriter['kriter'],
                hafta1=kriter.get('hafta1', 0),
                hafta2=kriter.get('hafta2', 0),
                hafta3=kriter.get('hafta3', 0),
                hafta4=kriter.get('hafta4', 0)
            )
            db.session.add(performans)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Performans verileri başarıyla kaydedildi'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
