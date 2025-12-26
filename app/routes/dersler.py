
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
    from app.models.kurs import Kurs
    from app.models.sinif import Sinif
    
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
    from app.models.kurs import Kurs
    from app.models.sinif import Sinif
    
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
        
        db.session.commit()
        flash('Ders bilgileri güncellendi!', 'success')
        return redirect(url_for('dersler.detay', id=ders.id))
    
    return render_template('dersler/form.html', form=form, ders=ders)


@bp.route('/secili')
@login_required
def secili_liste():
    """Seçili dersler listesi"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = Ders.query.filter_by(tur='secili')

    # Arama
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Ders.adi.like(f'%{search}%'),
                Ders.konu.like(f'%{search}%')
            )
        )

    # Sıralama
    query = query.order_by(Ders.tarih.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    dersler = pagination.items

    return render_template('dersler/liste.html',
                           dersler=dersler,
                           pagination=pagination,
                           search=search,
                           title='Seçili Dersler')


@bp.route('/ozel')
@login_required
def ozel_liste():
    """Özel dersler listesi"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = Ders.query.filter_by(tur='ozel')

    # Arama
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Ders.adi.like(f'%{search}%'),
                Ders.konu.like(f'%{search}%')
            )
        )

    # Sıralama
    query = query.order_by(Ders.tarih.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    dersler = pagination.items

    return render_template('dersler/liste.html',
                           dersler=dersler,
                           pagination=pagination,
                           search=search,
                           title='Özel Dersler')


@bp.route('/konular')
@login_required
def konu_liste():
    """Ders konuları listesi"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Tüm derslerdeki benzersiz konuları al
    konular_query = db.session.query(Ders.konu).filter(Ders.konu.isnot(None), Ders.konu != '').distinct()
    
    # Arama
    search = request.args.get('search', '')
    if search:
        konular_query = konular_query.filter(Ders.konu.like(f'%{search}%'))

    konular_query = konular_query.order_by(Ders.konu)
    
    # Sayfalama için konuları listeye çevir
    tum_konular = [k[0] for k in konular_query.all()]
    total = len(tum_konular)
    start = (page - 1) * per_page
    end = start + per_page
    konular = tum_konular[start:end]
    
    # Pagination objesi oluştur (manuel)
    class SimplePagination:
        def __init__(self, page, per_page, total):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None
    
    pagination = SimplePagination(page, per_page, total)

    return render_template('dersler/konular.html',
                           konular=konular,
                           pagination=pagination,
                           search=search)


@bp.route('/konu/ekle', methods=['GET', 'POST'])
@login_required
def konu_ekle():
    """Derse konu ekle"""
    from app.forms import DersKonuForm
    
    form = DersKonuForm()
    
    # Ders seçeneklerini yükle
    dersler = Ders.query.order_by(Ders.adi).all()
    form.ders_id.choices = [(d.id, d.adi) for d in dersler]
    
    if form.validate_on_submit():
        ders = Ders.query.get_or_404(form.ders_id.data)
        
        # Dersin mevcut konusunu güncelle veya ekle
        if ders.konu:
            # Eğer derse zaten konu varsa, yeni konu ekle (virgülle ayır)
            if form.konu.data not in ders.konu:
                ders.konu = ders.konu + ', ' + form.konu.data
        else:
            ders.konu = form.konu.data
        
        if form.aciklama.data:
            if ders.aciklama:
                ders.aciklama = ders.aciklama + ' | ' + form.aciklama.data
            else:
                ders.aciklama = form.aciklama.data
        
        db.session.commit()
        flash(f'"{form.konu.data}" konusu "{ders.adi}" dersine eklendi!', 'success')
        return redirect(url_for('dersler.konu_liste'))
    
    return render_template('dersler/konu_form.html', form=form)


@bp.route('/hafizlik')
@login_required
def hafizlik_liste():
    """Hafızlık dersleri listesi"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = Ders.query.filter_by(tur='hafizlik')

    # Arama
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Ders.adi.like(f'%{search}%'),
                Ders.konu.like(f'%{search}%')
            )
        )

    # Sıralama
    query = query.order_by(Ders.tarih.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    dersler = pagination.items

    return render_template('dersler/liste.html',
                           dersler=dersler,
                           pagination=pagination,
                           search=search,
                           title='Hafızlık Dersleri')


@bp.route('/hafizlik-dinleme')
@login_required
def hafizlik_dinleme_liste():
    """Hafızlık ders dinleme listesi"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = Ders.query.filter_by(tur='hafizlik_dinleme')

    # Arama
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Ders.adi.like(f'%{search}%'),
                Ders.konu.like(f'%{search}%')
            )
        )

    # Sıralama
    query = query.order_by(Ders.tarih.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    dersler = pagination.items

    return render_template('dersler/liste.html',
                           dersler=dersler,
                           pagination=pagination,
                           search=search,
                           title='Hafızlık Ders Dinleme')


@bp.route('/yuzune')
@login_required
def yuzune_liste():
    """Yüzüne dersleri listesi"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = Ders.query.filter_by(tur='yuzune')

    # Arama
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Ders.adi.like(f'%{search}%'),
                Ders.konu.like(f'%{search}%')
            )
        )

    # Sıralama
    query = query.order_by(Ders.tarih.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    dersler = pagination.items

    return render_template('dersler/liste.html',
                           dersler=dersler,
                           pagination=pagination,
                           search=search,
                           title='Yüzüne Dersleri')


@bp.route('/yuzune-oncesi')
@login_required
def yuzune_oncesi_liste():
    """Yüzüne öncesi dersleri listesi"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = Ders.query.filter_by(tur='yuzune_oncesi')

    # Arama
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Ders.adi.like(f'%{search}%'),
                Ders.konu.like(f'%{search}%')
            )
        )

    # Sıralama
    query = query.order_by(Ders.tarih.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    dersler = pagination.items

    return render_template('dersler/liste.html',
                           dersler=dersler,
                           pagination=pagination,
                           search=search,
                           title='Yüzüne Öncesi Dersleri')


@bp.route('/performans')
@login_required
def performans_liste():
    """Öğrenci performansları giriş sayfası"""
    from app.models.ogrenci import Ogrenci
    from app.models.kurs import Kurs
    from app.models.sinif import Sinif
    from app.models.performans import OgrenciPerformans
    from datetime import date
    
    # Filtreleme parametreleri
    veri_turu = request.args.get('veri_turu', 'gunluk')
    kurs_id = request.args.get('kurs_id', type=int)
    sinif_id = request.args.get('sinif_id', type=int)
    tarih_str = request.args.get('tarih', date.today().strftime('%Y-%m-%d'))
    
    try:
        tarih = datetime.strptime(tarih_str, '%Y-%m-%d').date()
    except:
        tarih = date.today()
    
    # Kurs ve sınıf listelerini hazırla
    if current_user.tur == 3:  # Kurs kullanıcısı
        kurslar = Kurs.query.filter_by(id=current_user.kaynak_id).all()
        kurs_id = current_user.kaynak_id
        siniflar = Sinif.query.filter_by(kurs_id=kurs_id).all()
    else:  # Admin
        kurslar = Kurs.query.filter_by(aktif=True).all()
        if kurs_id:
            siniflar = Sinif.query.filter_by(kurs_id=kurs_id).all()
        else:
            siniflar = Sinif.query.all()
    
    # Öğrencileri getir
    query = Ogrenci.query.filter_by(durum='aktif')
    
    if kurs_id:
        query = query.filter_by(kurs_id=kurs_id)
    if sinif_id:
        query = query.filter_by(sinif_id=sinif_id)
    
    ogrenciler = query.order_by(Ogrenci.adsoyad).all()
    
    # Her öğrenci için o gün/hafta performans verilerini al veya boş oluştur
    performans_data = {}
    for ogrenci in ogrenciler:
        perf = OgrenciPerformans.query.filter_by(
            ogrenci_id=ogrenci.id,
            tarih=tarih,
            veri_turu=veri_turu
        ).first()
        
        if not perf:
            # Eğer veri yoksa yeni bir kayıt oluştur (henüz kaydetme)
            perf = OgrenciPerformans(
                ogrenci_id=ogrenci.id,
                kurs_id=ogrenci.kurs_id,
                sinif_id=ogrenci.sinif_id,
                tarih=tarih,
                veri_turu=veri_turu
            )
        
        performans_data[ogrenci.id] = perf
    
    return render_template('dersler/performans.html',
                           ogrenciler=ogrenciler,
                           performans_data=performans_data,
                           kurslar=kurslar,
                           siniflar=siniflar,
                           veri_turu=veri_turu,
                           kurs_id=kurs_id,
                           sinif_id=sinif_id,
                           tarih=tarih)


@bp.route('/performans/kaydet', methods=['POST'])
@login_required
def performans_kaydet():
    """Öğrenci performans verilerini kaydet"""
    from app.models.performans import OgrenciPerformans
    from datetime import date
    
    try:
        data = request.get_json()
        ogrenci_id = data.get('ogrenci_id')
        tarih_str = data.get('tarih')
        veri_turu = data.get('veri_turu', 'gunluk')
        
        # Tarih parse et
        try:
            tarih = datetime.strptime(tarih_str, '%Y-%m-%d').date()
        except:
            tarih = date.today()
        
        # Var olan kaydı bul veya yeni oluştur
        performans = OgrenciPerformans.query.filter_by(
            ogrenci_id=ogrenci_id,
            tarih=tarih,
            veri_turu=veri_turu
        ).first()
        
        from app.models.ogrenci import Ogrenci
        ogrenci = Ogrenci.query.get(ogrenci_id)
        
        if not performans:
            performans = OgrenciPerformans(
                ogrenci_id=ogrenci_id,
                kurs_id=ogrenci.kurs_id,
                sinif_id=ogrenci.sinif_id,
                tarih=tarih,
                veri_turu=veri_turu
            )
            db.session.add(performans)
        
        # Puanları güncelle
        performans.ders_calisma_disiplini = data.get('ders_calisma_disiplini', 0)
        performans.ders_verme_performansi = data.get('ders_verme_performansi', 0)
        performans.sistem_uygulanma_disiplini = data.get('sistem_uygulanma_disiplini', 0)
        performans.ders_okuyus_hizi = data.get('ders_okuyus_hizi', 0)
        performans.talim_tecvid_durumu = data.get('talim_tecvid_durumu', 0)
        performans.ders_verme_zamanlamasi = data.get('ders_verme_zamanlamasi', 0)
        performans.sayfa_dinleme_disiplini = data.get('sayfa_dinleme_disiplini', 0)
        performans.kuran_kulturune_uyum = data.get('kuran_kulturune_uyum', 0)
        performans.hafta_basinda_kurs_zamanlamasi_giris = data.get('hafta_basinda_kurs_zamanlamasi_giris', 0)
        performans.ders_saatlerinde_sinifa_zamanlama_giris_mutabaa_saatleri = data.get('ders_saatlerinde_sinifa_zamanlama_giris_mutabaa_saatleri', 0)
        
        performans.kultur_saatlari_ders_zamanlama_giris = data.get('kultur_saatlari_ders_zamanlama_giris', 0)
        performans.sinif_hoca_ile_iletisim = data.get('sinif_hoca_ile_iletisim', 0)
        performans.arkadaslariyla_iletisim = data.get('arkadaslariyla_iletisim', 0)
        performans.namaz_vakitlerinde_mescide_zamanlama_giris = data.get('namaz_vakitlerinde_mescide_zamanlama_giris', 0)
        performans.ibadet_disiplini = data.get('ibadet_disiplini', 0)
        performans.kilkiyafet_disiplini = data.get('kilkiyafet_disiplini', 0)
        performans.yeme_icme_disiplini = data.get('yeme_icme_disiplini', 0)
        performans.yatalakhane_disiplini = data.get('yatalakhane_disiplini', 0)
        performans.trafic_kontrolu_kendini_cikisine_becerisi_temizlik_ve_duzen = data.get('trafic_kontrolu_kendini_cikisine_becerisi_temizlik_ve_duzen', 0)
        performans.genel_disiplin = data.get('genel_disiplin', 0)
        
        performans.notlar = data.get('notlar', '')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Performans verileri kaydedildi',
            'toplam_puan': performans.toplam_puan()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
