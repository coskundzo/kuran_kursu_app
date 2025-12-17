from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.ogrenci import Ogrenci
from app.models.egitmen import Egitmen
from app.models.kurs import Sinif, Kurs
from datetime import datetime

bp = Blueprint('ogrenciler', __name__, url_prefix='/ogrenciler')


@bp.route('/')
@login_required
def liste():
    """Öğrenci listesi"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Kullanıcının kurs filtresi
    query = Ogrenci.query
    
    if current_user.tur == 3:  # Kurs kullanıcısı
        query = query.filter_by(kurs_id=current_user.kaynak_id)
    elif current_user.tur == 4:  # Eğitmen
        egitmen = Egitmen.query.get(current_user.kaynak_id)
        if egitmen:
            query = query.filter_by(kurs_id=egitmen.kurs_id)
    
    # Arama
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Ogrenci.adsoyad.like(f'%{search}%'),
                Ogrenci.tc.like(f'%{search}%'),
                Ogrenci.sicil_no.like(f'%{search}%')
            )
        )
    
    # Durum filtresi
    durum = request.args.get('durum', '')
    if durum:
        query = query.filter_by(durum=durum)
    
    # Sınıf filtresi
    sinif_id = request.args.get('sinif_id', type=int)
    if sinif_id:
        query = query.filter_by(sinif_id=sinif_id)
    
    # Sıralama
    order_by = request.args.get('order_by', 'adsoyad')
    if order_by == 'adsoyad':
        query = query.order_by(Ogrenci.adsoyad)
    elif order_by == 'kayit_tarihi':
        query = query.order_by(Ogrenci.kayit_tarihi.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    ogrenciler = pagination.items
    
    # Sınıf listesi (filtreleme için)
    if current_user.tur == 3:
        siniflar = Sinif.query.filter_by(kurs_id=current_user.kaynak_id).all()
    else:
        siniflar = Sinif.query.all()
    
    return render_template('ogrenciler/liste.html',
                         ogrenciler=ogrenciler,
                         pagination=pagination,
                         siniflar=siniflar,
                         search=search,
                         durum=durum,
                         sinif_id=sinif_id)


@bp.route('/ekle', methods=['GET', 'POST'])
@login_required
def ekle():
    """Yeni öğrenci ekle"""
    if request.method == 'POST':
        try:
            # Kurs ID'sini belirle
            if current_user.tur == 3:
                kurs_id = current_user.kaynak_id
            else:
                kurs_id = request.form.get('kurs_id', type=int)
                if not kurs_id:
                    flash('Kurs seçimi zorunludur!', 'warning')
                    return redirect(url_for('ogrenciler.ekle'))
            
            ogrenci = Ogrenci(
                adsoyad=request.form.get('adsoyad'),
                tc=request.form.get('tc'),
                dogum_tarihi=datetime.strptime(request.form.get('dogum_tarihi'), '%Y-%m-%d').date() if request.form.get('dogum_tarihi') else None,
                cinsiyet=request.form.get('cinsiyet'),
                telefon=request.form.get('telefon'),
                email=request.form.get('email'),
                adres=request.form.get('adres'),
                veli_adi=request.form.get('veli_adi'),
                veli_telefon=request.form.get('veli_telefon'),
                veli_email=request.form.get('veli_email'),
                kurs_id=kurs_id,
                sinif_id=request.form.get('sinif_id', type=int),
                egitmen_id=request.form.get('egitmen_id', type=int),
                sicil_no=request.form.get('sicil_no'),
                egitim_turu=request.form.get('egitim_turu'),
                durum='aktif'
            )
            
            db.session.add(ogrenci)
            db.session.commit()
            
            flash('Öğrenci başarıyla eklendi!', 'success')
            return redirect(url_for('ogrenciler.liste'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'danger')
    
    # Form için gerekli listeler
    if current_user.tur == 3:  # Kurs kullanıcısı
        siniflar = Sinif.query.filter_by(kurs_id=current_user.kaynak_id).all()
        egitmenler = Egitmen.query.filter_by(kurs_id=current_user.kaynak_id).all()
        kurslar = []
    else:  # Admin veya diğer kullanıcılar
        siniflar = Sinif.query.all()
        egitmenler = Egitmen.query.all()
        kurslar = Kurs.query.filter_by(aktif=True).all()
    
    return render_template('ogrenciler/form.html',
                         ogrenci=None,
                         siniflar=siniflar,
                         egitmenler=egitmenler,
                         kurslar=kurslar)


@bp.route('/<int:id>')
@login_required
def detay(id):
    """Öğrenci detay sayfası"""
    ogrenci = Ogrenci.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and ogrenci.kurs_id != current_user.kaynak_id:
        flash('Bu öğrenciye erişim yetkiniz yok!', 'danger')
        return redirect(url_for('ogrenciler.liste'))
    
    return render_template('ogrenciler/detay.html', ogrenci=ogrenci)


@bp.route('/<int:id>/duzenle', methods=['GET', 'POST'])
@login_required
def duzenle(id):
    """Öğrenci düzenle"""
    ogrenci = Ogrenci.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and ogrenci.kurs_id != current_user.kaynak_id:
        flash('Bu öğrenciyi düzenleme yetkiniz yok!', 'danger')
        return redirect(url_for('ogrenciler.liste'))
    
    if request.method == 'POST':
        try:
            ogrenci.adsoyad = request.form.get('adsoyad')
            ogrenci.tc = request.form.get('tc')
            ogrenci.dogum_tarihi = datetime.strptime(request.form.get('dogum_tarihi'), '%Y-%m-%d').date() if request.form.get('dogum_tarihi') else None
            ogrenci.cinsiyet = request.form.get('cinsiyet')
            ogrenci.telefon = request.form.get('telefon')
            ogrenci.email = request.form.get('email')
            ogrenci.adres = request.form.get('adres')
            ogrenci.veli_adi = request.form.get('veli_adi')
            ogrenci.veli_telefon = request.form.get('veli_telefon')
            ogrenci.veli_email = request.form.get('veli_email')
            ogrenci.sinif_id = request.form.get('sinif_id', type=int)
            ogrenci.egitmen_id = request.form.get('egitmen_id', type=int)
            ogrenci.durum = request.form.get('durum')
            
            # Kurs bilgisi sadece admin ve müftü güncelleyebilir
            if current_user.tur in [1, 2]:
                kurs_id = request.form.get('kurs_id', type=int)
                if kurs_id:
                    ogrenci.kurs_id = kurs_id
            
            db.session.commit()
            
            flash('Öğrenci bilgileri güncellendi!', 'success')
            return redirect(url_for('ogrenciler.detay', id=ogrenci.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'danger')
    
    # Form için gerekli listeler
    if current_user.tur == 3:  # Kurs kullanıcısı
        siniflar = Sinif.query.filter_by(kurs_id=current_user.kaynak_id).all()
        egitmenler = Egitmen.query.filter_by(kurs_id=current_user.kaynak_id).all()
        # Kurs kullanıcısı kendi kursunu görsün ama değiştiremez
        kurs = Kurs.query.get(current_user.kaynak_id)
        kurslar = [kurs] if kurs else []
    else:  # Admin veya diğer kullanıcılar
        siniflar = Sinif.query.all()
        egitmenler = Egitmen.query.all()
        kurslar = Kurs.query.filter_by(aktif=True).all()
    
    return render_template('ogrenciler/form.html',
                         ogrenci=ogrenci,
                         siniflar=siniflar,
                         egitmenler=egitmenler,
                         kurslar=kurslar)


@bp.route('/<int:id>/sil', methods=['GET', 'POST'])
@login_required
def sil(id):
    """Öğrenci sil"""
    ogrenci = Ogrenci.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and ogrenci.kurs_id != current_user.kaynak_id:
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('ogrenciler.liste'))
    
    # İlişkili kayıtları kontrol et
    iliskili_kayitlar = []
    
    aidat_sayisi = ogrenci.aidat_hareketleri.count()
    if aidat_sayisi > 0:
        iliskili_kayitlar.append(f"{aidat_sayisi} aidat kaydı")
    
    yoklama_sayisi = ogrenci.yoklamalar.count()
    if yoklama_sayisi > 0:
        iliskili_kayitlar.append(f"{yoklama_sayisi} yoklama kaydı")
    
    # Hafızlık dersleri kontrolü
    from app.models.ders import HafizlikDers
    hafizlik_sayisi = HafizlikDers.query.filter_by(ogrenci_id=ogrenci.id).count()
    if hafizlik_sayisi > 0:
        iliskili_kayitlar.append(f"{hafizlik_sayisi} hafızlık ders kaydı")
    
    # Sınav sonuçları kontrolü
    sinav_sayisi = ogrenci.sinavlar.count()
    if sinav_sayisi > 0:
        iliskili_kayitlar.append(f"{sinav_sayisi} sınav sonucu")
    
    # GET isteği - onay sayfasını göster
    if request.method == 'GET':
        return render_template('ogrenciler/sil_onay.html', 
                             ogrenci=ogrenci, 
                             iliskili_kayitlar=iliskili_kayitlar)
    
    # POST isteği - silme işlemini gerçekleştir
    try:
        # İlişkili tüm kayıtları sil
        for aidat in ogrenci.aidat_hareketleri.all():
            db.session.delete(aidat)
        
        for yoklama in ogrenci.yoklamalar.all():
            db.session.delete(yoklama)
        
        for hafizlik in HafizlikDers.query.filter_by(ogrenci_id=ogrenci.id).all():
            db.session.delete(hafizlik)
        
        for sinav in ogrenci.sinavlar.all():
            db.session.delete(sinav)
        
        db.session.delete(ogrenci)
        db.session.commit()
        flash(f'{ogrenci.adsoyad} başarıyla silindi!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hata: {str(e)}', 'danger')
    
    return redirect(url_for('ogrenciler.liste'))


# Ön Kayıtlı Öğrenciler
@bp.route('/onkayit')
@login_required
def onkayit_liste():
    """Ön kayıtlı öğrenci listesi"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Kullanıcının kurs filtresi
    query = Ogrenci.query.filter_by(durum='onkayit')
    
    if current_user.tur == 3:  # Kurs kullanıcısı
        query = query.filter_by(kurs_id=current_user.kaynak_id)
    elif current_user.tur == 4:  # Eğitmen
        egitmen = Egitmen.query.get(current_user.kaynak_id)
        if egitmen:
            query = query.filter_by(kurs_id=egitmen.kurs_id)
    
    # Arama
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Ogrenci.adsoyad.like(f'%{search}%'),
                Ogrenci.tc.like(f'%{search}%'),
                Ogrenci.telefon.like(f'%{search}%')
            )
        )
    
    # Sıralama
    query = query.order_by(Ogrenci.kayit_tarihi.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    ogrenciler = pagination.items
    
    return render_template('ogrenciler/onkayit_liste.html',
                         ogrenciler=ogrenciler,
                         pagination=pagination,
                         search=search)


@bp.route('/onkayit/<int:id>')
@login_required
def onkayit_detay(id):
    """Ön kayıtlı öğrenci detay sayfası"""
    ogrenci = Ogrenci.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and ogrenci.kurs_id != current_user.kaynak_id:
        flash('Bu öğrenciye erişim yetkiniz yok!', 'danger')
        return redirect(url_for('ogrenciler.onkayit_liste'))
    
    if ogrenci.durum != 'onkayit':
        flash('Bu öğrenci ön kayıtlı değil!', 'warning')
        return redirect(url_for('ogrenciler.onkayit_liste'))
    
    return render_template('ogrenciler/onkayit_detay.html', ogrenci=ogrenci)


@bp.route('/onkayit/ekle', methods=['GET', 'POST'])
@login_required
def onkayit_ekle():
    """Ön kayıtlı öğrenci ekle"""
    if request.method == 'POST':
        try:
            # Kurs ID belirleme
            kurs_id = None
            if current_user.tur == 1:  # Admin
                kurs_id = request.form.get('kurs_id', type=int)
            elif current_user.tur == 3:  # Kurs kullanıcısı
                kurs_id = current_user.kaynak_id
            elif current_user.tur == 4:  # Eğitmen
                egitmen = Egitmen.query.get(current_user.kaynak_id)
                kurs_id = egitmen.kurs_id if egitmen else None
            
            if not kurs_id:
                flash('Kurs bilgisi alınamadı!', 'danger')
                return redirect(url_for('ogrenciler.onkayit_liste'))
            
            # Tarih formatını düzelt
            dogum_tarihi_str = request.form.get('dogum_tarihi')
            dogum_tarihi = None
            if dogum_tarihi_str:
                try:
                    dogum_tarihi = datetime.strptime(dogum_tarihi_str, '%Y-%m-%d').date()
                except:
                    pass
            
            ogrenci = Ogrenci(
                adsoyad=request.form.get('adsoyad'),
                tc=request.form.get('tc'),
                dogum_tarihi=dogum_tarihi,
                dogum_yeri=request.form.get('dogum_yeri'),
                cinsiyet=request.form.get('cinsiyet'),
                telefon=request.form.get('telefon'),
                email=request.form.get('email'),
                adres=request.form.get('adres'),
                veli_adi=request.form.get('veli_adi'),
                veli_telefon=request.form.get('veli_telefon'),
                veli_email=request.form.get('veli_email'),
                kurs_id=kurs_id,
                durum='onkayit',
                kayit_tarihi=datetime.now().date()
            )
            
            db.session.add(ogrenci)
            db.session.commit()
            flash(f'{ogrenci.adsoyad} ön kayıt olarak başarıyla eklendi!', 'success')
            return redirect(url_for('ogrenciler.onkayit_liste'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hata: {str(e)}', 'danger')
    
    # GET isteği
    kurslar = []
    if current_user.tur == 1:  # Admin
        kurslar = Kurs.query.filter_by(aktif=True).all()
    
    return render_template('ogrenciler/onkayit_form.html', 
                         ogrenci=None,
                         kurslar=kurslar)


@bp.route('/onkayit/<int:id>/duzenle', methods=['GET', 'POST'])
@login_required
def onkayit_duzenle(id):
    """Ön kayıtlı öğrenci düzenle"""
    ogrenci = Ogrenci.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and ogrenci.kurs_id != current_user.kaynak_id:
        flash('Bu öğrenciye erişim yetkiniz yok!', 'danger')
        return redirect(url_for('ogrenciler.onkayit_liste'))
    
    if ogrenci.durum != 'onkayit':
        flash('Bu öğrenci ön kayıtlı değil!', 'warning')
        return redirect(url_for('ogrenciler.onkayit_liste'))
    
    if request.method == 'POST':
        try:
            # Tarih formatını düzelt
            dogum_tarihi_str = request.form.get('dogum_tarihi')
            dogum_tarihi = None
            if dogum_tarihi_str:
                try:
                    dogum_tarihi = datetime.strptime(dogum_tarihi_str, '%Y-%m-%d').date()
                except:
                    pass
            
            ogrenci.adsoyad = request.form.get('adsoyad')
            ogrenci.tc = request.form.get('tc')
            ogrenci.dogum_tarihi = dogum_tarihi
            ogrenci.dogum_yeri = request.form.get('dogum_yeri')
            ogrenci.cinsiyet = request.form.get('cinsiyet')
            ogrenci.telefon = request.form.get('telefon')
            ogrenci.email = request.form.get('email')
            ogrenci.adres = request.form.get('adres')
            ogrenci.veli_adi = request.form.get('veli_adi')
            ogrenci.veli_telefon = request.form.get('veli_telefon')
            ogrenci.veli_email = request.form.get('veli_email')
            
            if current_user.tur == 1:  # Admin
                kurs_id = request.form.get('kurs_id', type=int)
                if kurs_id:
                    ogrenci.kurs_id = kurs_id
            
            db.session.commit()
            flash(f'{ogrenci.adsoyad} başarıyla güncellendi!', 'success')
            return redirect(url_for('ogrenciler.onkayit_liste'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hata: {str(e)}', 'danger')
    
    # GET isteği
    kurslar = []
    if current_user.tur == 1:  # Admin
        kurslar = Kurs.query.filter_by(aktif=True).all()
    
    return render_template('ogrenciler/onkayit_form.html', 
                         ogrenci=ogrenci,
                         kurslar=kurslar)


@bp.route('/onkayit/<int:id>/sil', methods=['POST'])
@login_required
def onkayit_sil(id):
    """Ön kayıtlı öğrenci sil"""
    ogrenci = Ogrenci.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and ogrenci.kurs_id != current_user.kaynak_id:
        flash('Bu öğrenciye erişim yetkiniz yok!', 'danger')
        return redirect(url_for('ogrenciler.onkayit_liste'))
    
    if ogrenci.durum != 'onkayit':
        flash('Bu öğrenci ön kayıtlı değil!', 'warning')
        return redirect(url_for('ogrenciler.onkayit_liste'))
    
    try:
        adsoyad = ogrenci.adsoyad
        db.session.delete(ogrenci)
        db.session.commit()
        flash(f'{adsoyad} ön kayıttan başarıyla silindi!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hata: {str(e)}', 'danger')
    
    return redirect(url_for('ogrenciler.onkayit_liste'))


@bp.route('/onkayit/<int:id>/aktif-et', methods=['POST'])
@login_required
def onkayit_aktif_et(id):
    """Ön kayıtlı öğrenciyi aktif yap"""
    ogrenci = Ogrenci.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and ogrenci.kurs_id != current_user.kaynak_id:
        flash('Bu öğrenciye erişim yetkiniz yok!', 'danger')
        return redirect(url_for('ogrenciler.onkayit_liste'))
    
    if ogrenci.durum != 'onkayit':
        flash('Bu öğrenci ön kayıtlı değil!', 'warning')
        return redirect(url_for('ogrenciler.onkayit_liste'))
    
    try:
        ogrenci.durum = 'aktif'
        
        # Sicil no oluştur
        if not ogrenci.sicil_no:
            son_sicil = Ogrenci.query.filter(
                Ogrenci.sicil_no.isnot(None),
                Ogrenci.kurs_id == ogrenci.kurs_id
            ).order_by(Ogrenci.sicil_no.desc()).first()
            
            if son_sicil and son_sicil.sicil_no:
                try:
                    son_numara = int(son_sicil.sicil_no.split('-')[-1])
                    yeni_numara = son_numara + 1
                except:
                    yeni_numara = 1
            else:
                yeni_numara = 1
            
            ogrenci.sicil_no = f'OGR-{yeni_numara:04d}'
        
        db.session.commit()
        flash(f'{ogrenci.adsoyad} başarıyla aktif öğrenci yapıldı!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hata: {str(e)}', 'danger')
    
    return redirect(url_for('ogrenciler.onkayit_liste'))


# Mezunlar
@bp.route('/mezunlar')
@login_required
def mezun_liste():
    """Mezun öğrenci listesi"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Kullanıcının kurs filtresi
    query = Ogrenci.query.filter_by(durum='mezun')
    
    if current_user.tur == 3:  # Kurs kullanıcısı
        query = query.filter_by(kurs_id=current_user.kaynak_id)
    elif current_user.tur == 4:  # Eğitmen
        egitmen = Egitmen.query.get(current_user.kaynak_id)
        if egitmen:
            query = query.filter_by(kurs_id=egitmen.kurs_id)
    
    # Arama
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Ogrenci.adsoyad.like(f'%{search}%'),
                Ogrenci.tc.like(f'%{search}%'),
                Ogrenci.sicil_no.like(f'%{search}%')
            )
        )
    
    # Sıralama
    query = query.order_by(Ogrenci.updated_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    ogrenciler = pagination.items
    
    return render_template('ogrenciler/mezun_liste.html',
                         ogrenciler=ogrenciler,
                         pagination=pagination,
                         search=search)


@bp.route('/mezunlar/<int:id>')
@login_required
def mezun_detay(id):
    """Mezun öğrenci detay sayfası"""
    ogrenci = Ogrenci.query.get_or_404(id)
    
    # Yetki kontrolü
    if current_user.tur == 3 and ogrenci.kurs_id != current_user.kaynak_id:
        flash('Bu öğrenciye erişim yetkiniz yok!', 'danger')
        return redirect(url_for('ogrenciler.mezun_liste'))
    
    if ogrenci.durum != 'mezun':
        flash('Bu öğrenci mezun değil!', 'warning')
        return redirect(url_for('ogrenciler.mezun_liste'))
    
    return render_template('ogrenciler/mezun_detay.html', ogrenci=ogrenci)


# API Endpoints
@bp.route('/api/<int:id>')
@login_required
def api_getir(id):
    """Öğrenci bilgilerini JSON olarak döndür"""
    ogrenci = Ogrenci.query.get_or_404(id)
    return jsonify(ogrenci.to_dict())
