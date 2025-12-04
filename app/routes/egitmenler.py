

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
