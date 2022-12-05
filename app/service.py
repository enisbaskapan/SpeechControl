from app.utils import Assemble, Obtain, Apply
from app.nlp.vocabulary import *


class Extract(Assemble, Obtain, Apply):
    """
    Extract information from the received request and return a url as a response
    """
    def __init__(self):
        
        super().__init__()
        
        self.response_content = {}
        
        self.response_content['date0'] = ""
        self.response_content['date1'] = ""

        self.response_content['from0'] = ""
        self.response_content['to0'] = ""
        
        self.response_content['from1'] = ""
        self.response_content['to1'] = ""
        
        self.response_content['Passengers'] = []
        
        self.response_content['no_stations'] = False
        
        self.entity_list = {'DURAK':station_list,
                            'AY':month_list,
                            'YOLCU':passenger_list,
                            'GÜN':weekday_list,
                            'SELF':self_list,
                            'DELAY':delay_list,
                            'SDELAY':s_delay_list,
                            'CİNSİYET':gender_list,
                            'SAYI':number_list}
        
    def extract_entities(self, doc):
        
        stations = []
        months = []
        passenger_types = []
        weekdays = []
        self_ = []
        delays = []
        s_delays = []
        genders = []
        numbers = []
        
        for index, ent in enumerate(doc.ents):
            label = ent.label_
            ent_list = self.entity_list[label]
            
            if label == 'DURAK' or label == 'AY' or label == 'GÜN' or label == 'SAYI':
                ent = self.apply_lemmatization_model(str(ent))
                
            if label== 'YOLCU':
                ent = str(ent).split(',')[0]
                if " " not in str(ent):
                    ent = self.apply_lemmatization_model(str(ent))

            if label != 'DURAK' and label != 'AY':
                ent = str(ent).lower()
                
            if str(ent) in ent_list:
                if label == 'DURAK': stations.append(str(ent)) 

                if label == 'AY': months.append((str(ent),index))

                if label == 'YOLCU': passenger_types.append((str(ent),index)) 

                if label == 'GÜN': weekdays.append(str(ent)) 

                if label == 'SELF': self_.append(str(ent)) 
                
                if label == 'DELAY': delays.append((str(ent),index))

                if label == 'SDELAY': s_delays.append((str(ent),index))
                
                if label == 'CİNSİYET': genders.append((str(ent),index)) 
                
                if label == 'SAYI': numbers.append((int(str(ent)),index))   
                
        dates, passengers, sdelays = self.obtain_indexes(months, passenger_types, s_delays, numbers)        
        dates, weekdays, delays, sdelays = self.process_datetime(dates, weekdays, delays, sdelays)
        
        entities = {'station':stations, 
                    'dates':dates, 
                    'weekdays':weekdays, 
                    'delays':delays,
                    'sdelays':sdelays, 
                    'passengers':passengers, 
                    'self':self_, 
                    'genders':genders}
        return entities
                
    def extract_stations(self, entities, defaultLocation):
        
        stations = entities['station']
        self.response_content = self.process_stations(stations, defaultLocation)
        return self.response_content
            
    def extract_dates(self, entities):
        
        dates = entities['dates']
        weekdays = entities['weekdays']
        delays = entities['delays']
        sdelays = entities['sdelays']
        
        self.response_content = self.process_dates(dates, weekdays)
        self.response_content = self.process_delays(delays, sdelays)
        return self.response_content
    
    def extract_passengers(self, entities):
        
        passengers = entities['passengers']
        self_ = entities['self']
        genders = entities['genders']
        
        self.response_content = self.process_passengers(passengers)
        self.response_content = self.process_self(self_)
        return self.response_content
        
    def extract(self, request_): 
        
        text = request_['text']
        defaultLocation =  request_['defaultLocation']
        
        doc = self.apply_ner_model(text)
        entities = self.extract_entities(doc)
        
        self.response_content = self.extract_dates(entities)
        self.response_content = self.extract_stations(entities, defaultLocation)
        self.response_content = self.extract_passengers(entities)
        
        self.response_content = self.compare_dates(self.response_content)
        self.response_content, self.response = self.process_available_stations(self.response_content, self.response)
        self.response = self.assemble_url()
        self.response = self.process_url(self.response)
        
        return self.response