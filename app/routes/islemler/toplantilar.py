
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.forms import ToplantiForm

# Blueprint oluşturuluyor
toplantilar_bp = Blueprint('toplantilar', __name__, url_prefix='/islemler/toplantilar')

# Toplantı listesi (örnek veri)
toplantilar = []

@toplantilar_bp.route('/')
def liste():
    return render_template('islemler/toplantilar_liste.html', toplantilar=toplantilar)

@toplantilar_bp.route('/ekle', methods=['GET', 'POST'])
def ekle():
    form = ToplantiForm()
    if form.validate_on_submit():
        konu = form.konu.data
        tarih = form.tarih.data.strftime('%Y-%m-%d')
        aciklama = form.aciklama.data
        toplantilar.append({'konu': konu, 'tarih': tarih, 'aciklama': aciklama})
        flash('Toplantı başarıyla eklendi.', 'success')
        return redirect(url_for('toplantilar.liste'))
    return render_template('islemler/toplantilar_form.html', form=form)

@toplantilar_bp.route('/sil/<int:id>', methods=['POST'])
def sil(id):
    if 0 <= id < len(toplantilar):
        toplantilar.pop(id)
        flash('Toplantı silindi.', 'success')
    else:
        flash('Toplantı bulunamadı.', 'danger')
    return redirect(url_for('toplantilar.liste'))

@toplantilar_bp.route('/duzenle/<int:id>', methods=['GET', 'POST'])
def duzenle(id):
    if 0 <= id < len(toplantilar):
        form = ToplantiForm(data=toplantilar[id])
        if form.validate_on_submit():
            toplantilar[id]['konu'] = form.konu.data
            toplantilar[id]['tarih'] = form.tarih.data.strftime('%Y-%m-%d')
            toplantilar[id]['aciklama'] = form.aciklama.data
            flash('Toplantı güncellendi.', 'success')
            return redirect(url_for('toplantilar.liste'))
        return render_template('islemler/toplantilar_form.html', form=form, id=id)
    flash('Toplantı bulunamadı.', 'danger')
    return redirect(url_for('toplantilar.liste'))
