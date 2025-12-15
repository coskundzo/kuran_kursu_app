

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.egitmen import Egitmen
from app.models.kurs import Kurs
from app.forms import EgitmenForm

bp = Blueprint('egitmenler', __name__, url_prefix='/egitmenler')

@bp.route('/')
@login_required
def liste():
    egitmenler = Egitmen.query.all()
    return render_template('egitmenler/liste.html', egitmenler=egitmenler)

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
