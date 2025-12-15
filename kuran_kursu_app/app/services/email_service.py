from flask_mail import Message
from flask import current_app, render_template
from app import mail


class EmailService:
    """Email Gönderim Servisi"""
    
    @staticmethod
    def gonder(alici, konu, mesaj, html=True):
        """
        Email gönder
        
        Args:
            alici: Alıcı email adresi (str veya list)
            konu: Email konusu
            mesaj: Email içeriği
            html: HTML formatında mı (bool)
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            msg = Message(
                subject=konu,
                recipients=[alici] if isinstance(alici, str) else alici,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            if html:
                msg.html = mesaj
            else:
                msg.body = mesaj
            
            mail.send(msg)
            return True
        
        except Exception as e:
            current_app.logger.error(f'Email gönderim hatası: {str(e)}')
            return False
    
    @staticmethod
    def gonder_template(alici, konu, template, **kwargs):
        """
        Template kullanarak email gönder
        
        Args:
            alici: Alıcı email adresi
            konu: Email konusu
            template: Template dosya adı (emails/ klasöründe)
            **kwargs: Template'e gönderilecek değişkenler
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            html = render_template(f'emails/{template}', **kwargs)
            return EmailService.gonder(alici, konu, html, html=True)
        except Exception as e:
            current_app.logger.error(f'Email template hatası: {str(e)}')
            return False
    
    @staticmethod
    def ogrenci_kayit_bildirimi(ogrenci, veli_email):
        """Öğrenci kayıt bildirimi gönder"""
        konu = f"{ogrenci.adsoyad} - Kayıt Onayı"
        mesaj = f"""
        <h2>Sayın Veli,</h2>
        <p>{ogrenci.adsoyad} adlı öğrencinizin kaydı başarıyla tamamlanmıştır.</p>
        <p><strong>Sicil No:</strong> {ogrenci.sicil_no}</p>
        <p><strong>Kayıt Tarihi:</strong> {ogrenci.kayit_tarihi.strftime('%d.%m.%Y')}</p>
        <p>Bilginize sunarız.</p>
        """
        return EmailService.gonder(veli_email, konu, mesaj)
    
    @staticmethod
    def aidat_hatirlatma(ogrenci, veli_email, tutar, vade_tarihi):
        """Aidat hatırlatma maili gönder"""
        konu = f"{ogrenci.adsoyad} - Aidat Hatırlatması"
        mesaj = f"""
        <h2>Sayın Veli,</h2>
        <p>{ogrenci.adsoyad} adlı öğrencinizin {tutar} TL tutarındaki aidat ödemesinin vadesi yaklaşmaktadır.</p>
        <p><strong>Vade Tarihi:</strong> {vade_tarihi.strftime('%d.%m.%Y')}</p>
        <p>Ödemenizi zamanında yapmanızı rica ederiz.</p>
        """
        return EmailService.gonder(veli_email, konu, mesaj)


# Helper function
def email_gonder(alici, konu, mesaj, html=True):
    """Email gönder (kısa yol)"""
    return EmailService.gonder(alici, konu, mesaj, html)
