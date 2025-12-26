# Model dosyası, uygulama başlatma içermez. Sadece model tanımları ve importları olmalı.
from app.models.user import User
from app.models.ogrenci import Ogrenci
from app.models.egitmen import Egitmen
from app.models.kurs import Kurs, Muftuluk
from app.models.ders import Ders, HafizlikDers
from app.models.sinif import Sinif
from app.models.karne import KarneSablon, KarneSablonEleman
from app.models.performans import OgrenciPerformans
from app.models.egitmen_performans import EgitmenPerformans