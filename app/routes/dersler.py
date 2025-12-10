
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.ders import Ders
from datetime import datetime

bp = Blueprint('dersler', __name__, url_prefix='/dersler')



@bp.route('/')
@login_required
def liste():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = Ders.query

    # Arama
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Ders.adi.like(f'%{search}%'),
                Ders.konu.like(f'%{search}%')
            )
        )

    # Tür filtresi
    tur = request.args.get('tur', '')
    if tur:
        query = query.filter_by(tur=tur)

    # Sıralama
    query = query.order_by(Ders.tarih.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    dersler = pagination.items

    return render_template('dersler/liste.html',
                           dersler=dersler,
                           pagination=pagination,
                           search=search,
                           tur=tur)


@bp.route('/ekle', methods=['GET', 'POST'])
@login_required
def ekle():
    from app.forms import DersForm
    from app.models.egitmen import Egitmen
    from app.models.kurs import Kurs, Sinif
    
    form = DersForm()
    
    # Dropdown verilerini yükle
    if current_user.tur == 3:  # Kurs kullanıcısı
        kurslar = [(current_user.kaynak_id, Kurs.query.get(current_user.kaynak_id).adi)]
        siniflar = [(s.id, s.adi) for s in Sinif.query.filter_by(kurs_id=current_user.kaynak_id).all()]
        egitmenler = [(e.id, e.adsoyad) for e in Egitmen.query.filter_by(kurs_id=current_user.kaynak_id).all()]
        # Kurs kullanıcısı için kurs otomatik seçili
        form.kurs_id.choices = kurslar
    else:  # Admin
        kurslar = [(k.id, k.adi) for k in Kurs.query.filter_by(aktif=True).all()]
        siniflar = [(s.id, s.adi) for s in Sinif.query.all()]
        egitmenler = [(e.id, e.adsoyad) for e in Egitmen.query.all()]
        form.kurs_id.choices = kurslar
    
    form.sinif_id.choices = [('', 'Seçiniz')] + siniflar
    form.egitmen_id.choices = [('', 'Seçiniz')] + egitmenler
    
    if form.validate_on_submit():
        # Kurs ID'sini belirle
        if current_user.tur == 3:
            kurs_id = current_user.kaynak_id
        else:
            kurs_id = form.kurs_id.data
        
        ders = Ders(
            adi=form.adi.data,
            kurs_id=kurs_id,
            sinif_id=form.sinif_id.data if form.sinif_id.data else None,
            egitmen_id=form.egitmen_id.data if form.egitmen_id.data else None,
            tur=form.tur.data,
            konu=form.konu.data,
            aciklama=form.aciklama.data,
            tarih=datetime.today()
        )
        db.session.add(ders)
        db.session.commit()
        flash('Ders başarıyla eklendi!', 'success')
        return redirect(url_for('dersler.liste'))
    return render_template('dersler/form.html', form=form)

@bp.route('/<int:id>')
@login_required
def detay(id):
    """Ders detay sayfası"""
    ders = Ders.query.get_or_404(id)
    return render_template('dersler/detay.html', ders=ders)

@bp.route('/<int:id>/duzenle', methods=['GET', 'POST'])
@login_required
def duzenle(id):
    """Ders düzenle"""
    from app.forms import DersForm
    from app.models.egitmen import Egitmen
    from app.models.kurs import Kurs, Sinif
    
    ders = Ders.query.get_or_404(id)
    form = DersForm(obj=ders)
    
    # Dropdown verilerini yükle
    if current_user.tur == 3:  # Kurs kullanıcısı
        kurslar = [(current_user.kaynak_id, Kurs.query.get(current_user.kaynak_id).adi)]
        siniflar = [(s.id, s.adi) for s in Sinif.query.filter_by(kurs_id=current_user.kaynak_id).all()]
        egitmenler = [(e.id, e.adsoyad) for e in Egitmen.query.filter_by(kurs_id=current_user.kaynak_id).all()]
        form.kurs_id.choices = kurslar
    else:  # Admin
        kurslar = [(k.id, k.adi) for k in Kurs.query.filter_by(aktif=True).all()]
        siniflar = [(s.id, s.adi) for s in Sinif.query.all()]
        egitmenler = [(e.id, e.adsoyad) for e in Egitmen.query.all()]
        form.kurs_id.choices = kurslar
    
    form.sinif_id.choices = [('', 'Seçiniz')] + siniflar
    form.egitmen_id.choices = [('', 'Seçiniz')] + egitmenler
    
    if form.validate_on_submit():
        ders.adi = form.adi.data
        ders.kurs_id = form.kurs_id.data if current_user.tur != 3 else current_user.kaynak_id
        ders.sinif_id = form.sinif_id.data if form.sinif_id.data else None
        ders.egitmen_id = form.egitmen_id.data if form.egitmen_id.data else None
        ders.tur = form.tur.data
        ders.konu = form.konu.data
        ders.aciklama = form.aciklama.data
        
        db.session.commit()
        flash('Ders bilgileri güncellendi!', 'success')
        return redirect(url_for('dersler.detay', id=ders.id))
    
    return render_template('dersler/form.html', form=form, ders=ders)
