from sqlalchemy import func

# 1. Toplu veya tekil aidat borçlandırma
def borclandir(ogrenci_id, tutar, donem, aciklama, vade_tarihi):
    aidat = AidatHareket(
        ogrenci_id=ogrenci_id,
        tutar=-abs(float(tutar)),
        donem=donem,
        aciklama=aciklama,
        vade_tarihi=vade_tarihi,
        odendi=False
    )
    db.session.add(aidat)
    db.session.commit()
    return aidat

# 2. Aidat ödeme kaydı
def aidat_odeme(ogrenci_id, tutar, donem, aciklama, odeme_tarihi):
    aidat = AidatHareket(
        ogrenci_id=ogrenci_id,
        tutar=abs(float(tutar)),
        donem=donem,
        aciklama=aciklama,
        odendi=True,
        odeme_tarihi=odeme_tarihi
    )
    db.session.add(aidat)
    # Gelir hareketi eklenebilir: gelir = GelirHareket(...)
    db.session.commit()
    return aidat

# 3. Aidat silme
def aidat_sil(aidat_id):
    aidat = AidatHareket.query.get(aidat_id)
    if aidat:
        db.session.delete(aidat)
        # İlgili gelir kaydı da silinebilir
        db.session.commit()
        return True
    return False

# 4. Aidat listesi ve raporlama (filtreleme örneği)
def aidat_liste(ogrenci_id=None, donem=None, odendi=None):
    query = AidatHareket.query
    if ogrenci_id:
        query = query.filter_by(ogrenci_id=ogrenci_id)
    if donem:
        query = query.filter_by(donem=donem)
    if odendi is not None:
        query = query.filter_by(odendi=odendi)
    return query.order_by(AidatHareket.vade_tarihi.desc()).all()

# 5. Öğrenci borcu hesaplama
def ogrenci_bakiye(ogrenci_id):
    toplam = db.session.query(func.sum(AidatHareket.tutar)).filter_by(ogrenci_id=ogrenci_id).scalar()
    return toplam or 0

# 6. SMS ile bildirim (örnek fonksiyon)
def aidat_sms(aidat_id_list, mesaj):
    ogrenci_telefonlari = []
    for aidat_id in aidat_id_list:
        aidat = AidatHareket.query.get(aidat_id)
        if aidat and aidat.ogrenci and aidat.ogrenci.telefon:
            ogrenci_telefonlari.append(aidat.ogrenci.telefon)
    # SMS gönderme servisi ile entegre edilebilir
    # sms_service.send_bulk(ogrenci_telefonlari, mesaj)
    return ogrenci_telefonlari

# 7. Yetkilendirme örneği (view fonksiyonlarında kullanılır)
def aidat_yetki_kontrol():
    if current_user.tur not in [1, 2, 3]:
        flash('Aidat işlemleri için yetkiniz yok!', 'danger')
        return False
    return True


from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.ders import AidatHareket
from app.models.ogrenci import Ogrenci
from datetime import datetime

bp = Blueprint('aidat', __name__, url_prefix='/aidat')


@bp.route('/')
@login_required
def liste():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = AidatHareket.query

    # Arama
    search = request.args.get('search', '')
    if search:
        query = query.join(Ogrenci).filter(
            db.or_(
                Ogrenci.adsoyad.like(f'%{search}%'),
                Ogrenci.tc.like(f'%{search}%')
            )
        )

    # Durum filtresi
    odendi = request.args.get('odendi', '')
    if odendi == '1':
        query = query.filter_by(odendi=True)
    elif odendi == '0':
        query = query.filter_by(odendi=False)

    query = query.order_by(AidatHareket.vade_tarihi.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    aidatlar = pagination.items

    return render_template('aidat/liste.html',
                           aidatlar=aidatlar,
                           pagination=pagination,
                           search=search,
                           odendi=odendi)


@bp.route('/ekle', methods=['GET', 'POST'])
@login_required
def ekle():
    from app.forms import AidatForm
    from app.models.ders import AidatHareket
    from app.models.ogrenci import Ogrenci
    form = AidatForm()
    if form.validate_on_submit():
        ogrenci = Ogrenci.query.get(int(form.ogrenci_id.data))
        if not ogrenci:
            flash('Öğrenci bulunamadı!', 'danger')
            return render_template('aidat/form.html', form=form)
        aidat = AidatHareket(
            ogrenci_id=ogrenci.id,
            kurs_id=ogrenci.kurs_id,
            tutar=form.tutar.data,
            donem=form.donem.data,
            vade_tarihi=datetime.strptime(form.vade_tarihi.data, '%Y-%m-%d') if form.vade_tarihi.data else None,
            odendi=form.odendi.data,
            aciklama=form.aciklama.data
        )
        db.session.add(aidat)
        db.session.commit()
        flash('Aidat başarıyla eklendi!', 'success')
        return redirect(url_for('aidat.liste'))
    return render_template('aidat/form.html', form=form)
