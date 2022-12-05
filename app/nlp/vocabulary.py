import numpy as np

passenger_vocab = {"ADT":["yolcu", "yetişkin", "kişi","kendime","kendim"],
                                "CHD":["çocuk","çocuğum"],
                                "PET":["hayvan"],
                                "YNG":["öğrenci", "genç"],
                                "TCH":["öğretmen", "öğretim görevlisi"],
                                "PRS":['basın', 'muhabir'],
                                "MLT":['asker'],
                                "STF":['personel', 'çalışan'],
                                "60Y":['60 yaş'],
                                "65+":['65 yaş']}
station_vocab = {"Söğütlüçeşme":"SGTC",
                        "Ankara":"ANKR",
                        "İstanbul":"ISTN",
                        "Eskişehir":"ESKR",
                        "Polatlı":"PLTL"}

station_list = ['Ankara', 'İstanbul', 'Eskişehir', 'İzmir', 'Kars', 'Konya', 'Malatya', 'Adana', 'Polatlı', 'Söğütlüçeşme', 'Eryaman', 'Bakırköy', 'Bozüyük', 'Sakarya']
month_list = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
weekday_list = ['pazartesi', 'salı', 'çarşamba', 'perşembe', 'cuma', 'cumartesi', 'pazar']
self_list = ['ben', 'bana', 'benim adıma', 'kendim', 'kendime']
s_delay_list = ['güne', 'gün sonraya', 'gün sonrasına', 'gün ilerisine', 'ay', 'hafta', 'ayın', 'haftasına']
gender_list = ['erkek', 'kadın', 'kız', 'hanımefendi', 'beyefendi']
delay_list = ['haftaya', 'günübirlik', 'haftaya yarın', 'ertesi', 'ertesi gün', 'ertesi güne', 'yarın', 'yarına', 'yarın için', 'bugün', 'bugüne', 'haftaya bugün', 'sabaha', 'akşama', 'akşam için', 'sabah için', 'öğleye', 'öğlene', 'öğleden sonraya', 'öğleden sonrasına', 'hafta içi', 'hafta sonu']
passenger_list = ['yolcu', 'engelli', 'arkadaş', 'askeri personel', 'sakat', 'gazi', 'kişilik', 'kişiye', 'şehit yakını', 'gazi yakını', 'hamile', 'çocuklu', 'arkadaşım', 'veli', 'yetişkin', 'çocuğum', 'yaşlı', 'kişi', 'çocuk', 'hayvan', 'öğrenci', 'genç', 'öğretmen', 'öğretim görevlisi', 'basın', 'muhabir', 'asker', 'personel', 'çalışan', '60 yaş', '65 yaş']
number_list = list(np.arange(1,32).astype(str))
