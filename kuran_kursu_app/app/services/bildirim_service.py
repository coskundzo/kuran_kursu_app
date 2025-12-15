import requests
from flask import current_app


class BildirimService:
    """Firebase Cloud Messaging ile Push Bildirim Servisi"""
    
    @staticmethod
    def gonder(cihaz_jetonu, baslik, mesaj, data=None):
        """
        Push bildirim gönder
        
        Args:
            cihaz_jetonu: FCM device token
            baslik: Bildirim başlığı
            mesaj: Bildirim mesajı
            data: Ek veri (dict)
            
        Returns:
            bool: Başarılı ise True
        """
        fcm_key = current_app.config.get('FCM_SERVER_KEY')
        
        if not fcm_key or not cihaz_jetonu:
            return False
        
        url = 'https://fcm.googleapis.com/fcm/send'
        
        headers = {
            'Authorization': f'key={fcm_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'to': cihaz_jetonu,
            'notification': {
                'title': baslik,
                'body': mesaj,
                'sound': 'default',
                'vibrate': 1
            }
        }
        
        if data:
            payload['data'] = data
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )
            return response.status_code == 200
        
        except Exception as e:
            current_app.logger.error(f'Push bildirim hatası: {str(e)}')
            return False
    
    @staticmethod
    def toplu_gonder(cihaz_jetonlari, baslik, mesaj, data=None):
        """
        Toplu push bildirim gönder
        
        Args:
            cihaz_jetonlari: FCM device token listesi
            baslik: Bildirim başlığı
            mesaj: Bildirim mesajı
            data: Ek veri (dict)
            
        Returns:
            dict: {'basarili': int, 'basarisiz': int}
        """
        basarili = 0
        basarisiz = 0
        
        for jeton in cihaz_jetonlari:
            if BildirimService.gonder(jeton, baslik, mesaj, data):
                basarili += 1
            else:
                basarisiz += 1
        
        return {
            'basarili': basarili,
            'basarisiz': basarisiz
        }


# Helper function
def bildirim_gonder(cihaz_jetonu, baslik, mesaj, data=None):
    """Push bildirim gönder (kısa yol)"""
    return BildirimService.gonder(cihaz_jetonu, baslik, mesaj, data)
