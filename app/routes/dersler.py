
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
    form = DersForm()
    if form.validate_on_submit():
        ders = Ders(
            adi=form.adi.data,
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
