import requests
from flask import current_app
from app import db
from app.models.user import User


class SmsService:
    """SMS Gönderim Servisi"""
    
    def __init__(self, kullanici=None):
        """
        Args:
            kullanici: User modeli instance veya None (config'den alır)
        """
        self.kullanici = kullanici
        self.config = self._get_config()
    
    def _get_config(self):
        """SMS konfigürasyonunu al"""
        if self.kullanici and self.kullanici.sms_user:
            return {
                'user': self.kullanici.sms_user,
                'pass': self.kullanici.sms_pass,
                'title': self.kullanici.sms_title or 'EKURANKURSU',
                'provider': self.kullanici.sms_saglayici or 0,
                'apikey': self.kullanici.sms_apikey or ''
            }
        else:
            return {
                'user': current_app.config.get('SMS_USER'),
                'pass': current_app.config.get('SMS_PASSWORD'),
                'title': current_app.config.get('SMS_TITLE'),
                'provider': current_app.config.get('SMS_PROVIDER'),
                'apikey': current_app.config.get('SMS_API_KEY')
            }
    
    def gonder(self, telefon, mesaj):
        """
        SMS gönder
        
        Args:
            telefon: Telefon numarası (10 haneli)
            mesaj: SMS mesajı
            
        Returns:
            bool: Başarılı ise True
        """
        if not telefon or not mesaj:
            return False
        
        # Türkçe karakterleri temizle
        mesaj = self._turkce_temizle(mesaj)
        
        # Telefon numarasını temizle (son 10 hane)
        telefon = ''.join(filter(str.isdigit, telefon))[-10:]
        
        if len(telefon) != 10:
            return False
        
        # Provider'a göre gönder
        try:
            if self.config['provider'] == 2:  # Dakik SMS
                return self._dakik_sms(telefon, mesaj)
            elif self.config['provider'] == 7:  # NetGSM
                return self._netgsm(telefon, mesaj)
            else:
                return False
        except Exception as e:
            current_app.logger.error(f'SMS gönderim hatası: {str(e)}')
            return False
    
    def _dakik_sms(self, telefon, mesaj):
        """Dakik SMS ile gönder"""
        xml = f"""<SMS>
            <oturum>
                <kullanici>{self.config['user']}</kullanici>
                <sifre>{self.config['pass']}</sifre>
            </oturum>
            <mesaj>
                <baslik>{self.config['title']}</baslik>
                <metin>{mesaj}</metin>
                <alicilar>{telefon}</alicilar>
            </mesaj>
        </SMS>"""
        
        response = requests.post(
            'http://dakiksms.mobi/api/tr/xml_api.php',
            data=xml.encode('utf-8'),
            headers={'Content-Type': 'text/xml'},
            timeout=30
        )
        
        return response.status_code == 200
    
    def _netgsm(self, telefon, mesaj):
        """NetGSM ile gönder"""
        url = "http://api.netgsm.com.tr/bulkhttppost.asp"
        
        params = {
            'usercode': self.config['user'],
            'password': self.config['pass'],
            'gsmno': telefon,
            'message': mesaj,
            'msgheader': self.config['title']
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        # NetGSM 00 ile başlıyorsa başarılı
        return response.text.startswith('00')
    
    def _turkce_temizle(self, text):
        """Türkçe karakterleri İngilizce karakterlere çevir"""
        tr_chars = 'çÇöÖşŞıİğĞüÜ'
        en_chars = 'cCoOsSiIgGuU'
        
        trans_table = str.maketrans(tr_chars, en_chars)
        return text.translate(trans_table)
    
    def toplu_gonder(self, telefon_listesi, mesaj):
        """
        Toplu SMS gönder
        
        Args:
            telefon_listesi: Telefon numaraları listesi
            mesaj: SMS mesajı
            
        Returns:
            dict: {'basarili': int, 'basarisiz': int}
        """
        basarili = 0
        basarisiz = 0
        
        for telefon in telefon_listesi:
            if self.gonder(telefon, mesaj):
                basarili += 1
            else:
                basarisiz += 1
        
        return {
            'basarili': basarili,
            'basarisiz': basarisiz
        }


# Kısa yoldan kullanım için
def sms_gonder(telefon, mesaj, kullanici=None):
    """
    SMS gönder (helper function)
    
    Args:
        telefon: Telefon numarası
        mesaj: SMS mesajı
        kullanici: User instance (opsiyonel)
    
    Returns:
        bool: Başarılı ise True
    """
    service = SmsService(kullanici)
    return service.gonder(telefon, mesaj)
