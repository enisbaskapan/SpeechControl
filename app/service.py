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
        self.response_content['invalid_date'] = False

        self.entity_list = {'DURAK':station_list,
                            'AY':month_list,
                            'YOLCU':passenger_list,
                            'GÜN':weekday_list,
                            'SELF':self_list,
                            'DELAY':delay_list,
                            'SDELAY':s_delay_list,
                            'CİNSİYET':gender_list,
                            'SAYI':number_list}

    #@property
    #def extract_response_content_copy(self):
        
    def extract_entities(self, doc):
        
        entities = []
        
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
                
            if str(ent) in ent_list: entities.append((str(ent), index, label))   
                
        entities, final_entities = self.obtain_indexes(entities)
        final_entities = self.assemble_entities(entities, final_entities)
        
        return final_entities
                
    def extract_stations(self, entities, defaultLocation):
        
        stations = [station for station in entities if station[-1]=='DURAK']
        entities = [entity for entity in entities if entity not in stations]
        self.response_content = self.process_stations(stations, defaultLocation)
        return self.response_content, entities
            
    def extract_dates(self, entities):
        
        dates = [date for date in entities if len(date) > 2]
        entities = [entity for entity in entities if entity not in dates]
        self.response_content = self.process_dates(dates)
        
        return self.response_content, entities
    
    def extract_passengers(self, entities):
        
        passengers = entities
        self.response_content = self.process_passengers(passengers)
        return self.response_content
        
    def extract(self, request_): 
        
        text = request_['text']
        defaultLocation =  request_['defaultLocation']
        
        doc = self.apply_ner_model(text)
        entities = self.extract_entities(doc)
        
        self.response_content, entities = self.extract_stations(entities, defaultLocation)
        self.response_content, entities = self.extract_dates(entities)
        self.response_content = self.extract_passengers(entities)
        
        self.response_content = self.compare_dates(self.response_content)
        self.response_content, self.response = self.process_available_stations(self.response_content, self.response)
        self.response = self.assemble_url()
        self.response = self.process_url(self.response_content, self.response)

        return self.response

