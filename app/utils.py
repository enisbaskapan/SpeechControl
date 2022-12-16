import datetime
from spacy import load
from app.nlp.lemmatizer import lemmatizeWord
from app.nlp.vocabulary import *

class Transform:
    
    def transform_station_tags(self, response_content):

        if response_content['from0'] in station_vocab: response_content['from0'] = station_vocab[response_content['from0']]

        if response_content['from1'] in station_vocab: response_content['from1'] = station_vocab[response_content['from1']]

        if response_content['to0'] in station_vocab: response_content['to0'] = station_vocab[response_content['to0']]

        if response_content['to1'] in station_vocab: response_content['to1'] = station_vocab[response_content['to1']]

        if response_content['date1'] == "":
            del response_content['date1']
            del response_content['from1']
            del response_content['to1']
                
        return response_content

    def transform_passenger_tags(self, response_content):
        
        passenger_types = {}
        for passenger in response_content['Passengers']:
            for tag, types in passenger_vocab.items(): 
                #yolcu tipinin bulunduğu liste
                if passenger[1] in types:
                    passenger_tag = tag
                    passenger_count = passenger[0]
                    #eğer yolcu tagi listede varsa yolcu sayısını üstüne ekle
                    if passenger_tag in passenger_types.keys():
                        passenger_types[passenger_tag] += passenger_count
                    #yeni bir tagse yeni yolcu ekle
                    else:
                        passenger_types[passenger_tag] = passenger_count
                        
        del response_content['Passengers']
        
        for key, value in passenger_types.items():
            response_content[key] = str(value)
            
        return response_content
    
class Format:
    
    def __init__(self):
        
        self.today = datetime.date.today()
    
    def format_date_string(self, datetime_object):
        formatted_date_string = datetime_object.strftime("%d-%m-%Y")
        return formatted_date_string
    
    def format_weekdays(self, weekday):

        weekday_index = weekday_list.index(weekday[0])
        weekdays = self.today + datetime.timedelta((weekday_index-self.today.weekday()) % 7)
        return weekdays
    
    def format_tomorrow(self):
        
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        return tomorrow
    
    def format_delays(self, delay):
        
        word = delay[0]
        word = word.lower()
        
        if 'hafta' in word:
            date = self.today + datetime.timedelta(weeks=1)
            
        elif 'günübirlik' in word:
            date = self.today
        
        elif 'bugün' in word:
            date = self.today
            
        elif 'ertesi' in word or 'yarın' in word:
            date = self.today + datetime.timedelta(days=1)
            
        return date
    
    def format_sdelays(self, sdelay):
        #delay tagleri içerisinde geçen kelimeye göre hafta veya gün sonrasını alma
       
        word = sdelay[1]
        word = word.lower()
        
        if 'hafta' in word:
            date = datetime.timedelta(weeks=int(sdelay[0]))
            
        if 'gün' in word:
            date = datetime.timedelta(days=int(sdelay[0]))

        return date
    
    def format_date_object(self, date_object):
        """
        Convert datetime.date object into datetime.datetime object in order compute and compare dates
        
        Parameters
        ----------
        date_object: datetime.date
            datetime.date object
        
        """
        datetime_object = datetime.datetime.fromordinal(date_object.toordinal())
        return datetime_object
    
    def format_datetime(self, date):
        
        current_year = datetime.date.today().year
        formatted_date = datetime.datetime(current_year, month_list.index(str(date[1])) + 1, int(date[0]))

        return formatted_date
    
    def format_dates(self, date):
        
        formatted_dates = self.format_datetime(date)

        return formatted_dates

    def format_labels(self, date):
        
        label = date[-1]
        
        if label == 'AY':
            date = self.format_dates(date)
        if label == 'GÜN':
            date = self.format_weekdays(date)
        if label == 'DELAY':
            date = self.format_delays(date)
        if label == 'SDELAY':
            date = self.format_sdelays(date)
        if label == 'TMRW':
            date = self.format_tomorrow()

        return date

class Check(Format):
    
    def __init__(self):

        super().__init__()
        
    def check_date0(self, response_content):

        if not response_content['date0']:
            return True
        else:
            return False

    def check_return(self, response_content):

        if not response_content['date1']:
            return False
        else:
            return True

    def check_date_indexes(self, date0, date1): # True = check_daily()

        label0 = date0[-1]
        label1 = date1[-1]
        
        if label1 == 'SDELAY':
            date0 = self.format_labels(date0)
            # If both label0 and label1 are sdelay, date0 needs to be datetime.date so datetime.timedelta can be added to it.
            if label0 == label1: date0 = self.today + date0
            date1 = self.format_labels(date1)
            date1 = date0 + date1
        
        elif label0 == 'SDELAY':
            date0 = self.today + self.format_labels(date0)
            date1 = self.format_labels(date1)

        else:
            date0 = self.format_labels(date0)
            date1 = self.format_labels(date1)
        return date0, date1
    
    def check_date_index(self, date0):
        
        label = date0[-1]

        if label == 'SDELAY':
            date0 = self.format_labels(date0)
            date0 = self.today + date0
        else:
            date0 = self.format_labels(date0)
        return date0

class Compare(Check):
    
    def __init__(self):
        
        super().__init__()

    def compare_today(self, date0, date1):

        today = self.format_date_object(self.today)

        if date0 != "" and date0 < today:
            date0 = date0 + datetime.timedelta(days=365)
        if date1 != "" and date1 < today:
            date1 = date1 + datetime.timedelta(days=365)

        return date0, date1

    def compare_dates(self, response_content):
        
        date0 = response_content['date0']
        date1 = response_content['date1']
        return_date = self.check_return(response_content)
        
        if return_date:
            date0, date1 = self.check_date_indexes(date0, date1)
            date0 = self.format_date_object(date0)
            date1 = self.format_date_object(date1)
        else:
            date0 = self.check_date_index(date0)
            date0 = self.format_date_object(date0)
        # If date0 and date1 not empty,
        if date0 and date1:
            if date0 > date1:
                temp_date = date0
                date0 = date1
                date1 = temp_date
                
        if date0: date0 = self.format_date_string(date0)
        if date1: date1 = self.format_date_string(date1)

        response_content['date0'] = date0
        response_content['date1'] = date1
        
        return response_content
            
    def compare_weekdays(self, weekdays):
        
        weekdays = self.format_weekdays(weekdays)
   
        if len(weekdays) == 2 and weekdays[1] < weekdays[0]:
            weekdays[1] = weekdays[1] + datetime.timedelta(weeks=1)
      
        return weekdays

class Process(Compare, Check):
    
    def __init__(self):
        
        super().__init__()
        
    def process_dates(self, dates):
    
        date_dict = {}
        for date in dates:
            key = date[-2]
            date_dict[key] = date
                
        if len(date_dict) !=0: self.response_content['date0'] = date_dict[min(date_dict.keys())]
        if len(date_dict) > 1: self.response_content['date1'] = date_dict[max(date_dict.keys())]
        return self.response_content
   
    def process_stations(self, stations, defaultLocation):
        
        if len(stations) == 2:
            From, To = stations
            From = From[0]
            To = To[0]
            self.response_content['from0'] = From
            self.response_content['to0'] = To
            
            self.response_content['from1'] = To
            self.response_content['to1'] = From
            
        elif len(stations) == 1: 
            
            # Assign default_location as the departure location that is retrieved from0 GPS
            From, To = defaultLocation, stations[0]
            To = To[0]
            self.response_content['from0'] = From
            self.response_content['to0'] = To
            
            self.response_content['from1'] = To
            self.response_content['to1'] = From
            
        return self.response_content
                    
    def process_passengers(self, passengers):
        
        self.response_content['Passengers'] = passengers
        return self.response_content

    def process_self(self, self_):
        
        if len(self_) != 0:
            self.response_content['Passengers'].append((1, self_[0]))
        return self.response_content
 
    def process_available_stations(self, response_content, response):
        
        if response_content['from0'] == "" and response_content['from1'] == "": self.response_content['no_stations'] = True
        else: self.response_content['no_stations'] = False
        
        if response_content['no_stations']:
            response['exampleArrival']['stationList'] = list(station_vocab.keys())
            
        
        #del response_content['no_stations']
        response_content.pop('no_stations')
        
        if response_content['from0'] == response_content['to0']:
            response['exampleArrival']['stationList'] = list(station_vocab.keys())
            
        return response_content, response
    
    def process_url(self, response):
        if response['exampleArrival']["stationList"] != [""]:
            response['url'] = ""
        return response

class Assemble(Process, Transform):
    
    def __init__(self):
        
        super().__init__()

        self.response = {}
        
        #self.response['exampleDeparture'] = {}
        self.response['exampleArrival'] = {}
        
        #self.response['exampleDeparture']["message"] = "Lütfen gitmek istediğiniz durağı belirtin."
        #self.response['exampleDeparture']["stationList"] = [""]
        
        self.response['exampleArrival']["message"] = "Lütfen geçerli bir durak belirtiniz."
        self.response['exampleArrival']["stationList"] = [""]
        
        self.response['url'] = ""
    
    def assemble_url(self): 
    
        
        self.response_content = self.transform_station_tags(self.response_content)
        self.response_content = self.transform_passenger_tags(self.response_content)

        link = "/availability?"

        for key, value in self.response_content.items():
            link = link+key+"="+value+"&"
            
        #linkteki son & işaretini alma
        link = link[:-1]
        self.response['url'] = link 
        return self.response
    
    def assemble_entities(self, entities, final_entities):
        
        for entity in entities:
            if entity[-1] != "":
                final_entities.append(entity)
        
        return final_entities
        
    
class Obtain:
    
    def obtain_dates(self, entities, final_entities):

        for index, entity in enumerate(entities):
            name = entity[0]
            label = entity[-1]
            prev = index-1
            next_ = index+1
            if label == 'AY':
                if index > 0 and entities[prev][2] == 'SAYI':
                    final_entities.append((entities[prev][0], name, index, label))
                    entities.pop(prev)
                    entities.insert(prev,("","",""))
                    entities.pop(index)
                    entities.insert(index,("","",""))
                elif index < len(entities)-1 and entities[next_][2] == 'SAYI':
                    final_entities.append((entities[next_][0], name, index, label))
                    entities.pop(next_)
                    entities.insert(next_,("","",""))
                    entities.pop(index)
                    entities.insert(index,("","",""))
                    
        return entities, final_entities

    def obtain_sdelays(self, entities, final_entities):

        for index, entity in enumerate(entities):
            name = entity[0]
            label = entity[-1]
            prev = index-1
            next_ = index+1
            if label == 'SDELAY':
                if index > 0 and entities[prev][2] == 'SAYI':
                    final_entities.append((entities[prev][0], name, index, label))
                    entities.pop(prev)
                    entities.insert(prev,("","",""))
                    entities.pop(index)
                    entities.insert(index,("","",""))
                elif index < len(entities)-1 and entities[next_][2] == 'SAYI':
                    final_entities.append((entities[next_][0], name, index, label))
                    entities.pop(next_)
                    entities.insert(next_,("","",""))
                    entities.pop(index)
                    entities.insert(index,("","",""))

        return entities, final_entities

    def obtain_passengers(self, entities, final_entities):

        for index, entity in enumerate(entities):
            name = entity[0]
            label = entity[-1]
            prev = index-1
            if label == 'YOLCU':
                if index > 0 and entities[prev][2] == 'SAYI':
                    final_entities.append((entities[prev][0], name))
                    entities.pop(prev)
                    entities.insert(prev,("","",""))
                    entities.pop(index)
                    entities.insert(index,("","",""))
                else:
                    final_entities.append((1, name))
                    
            if label == 'SELF':
                final_entities.append((1, name))
                
        return entities, final_entities
    
    def obtain_indexes(self, entities):
        
        final_entities = []
        entities, final_entities = self.obtain_dates(entities, final_entities)
        entities, final_entities = self.obtain_sdelays(entities, final_entities)
        entities, final_entities = self.obtain_passengers(entities, final_entities)

        return entities, final_entities
    
class Apply:
    
    def apply_ner_model(self, text):
        ner_model = load('./app/nlp/model-best')
        doc = ner_model(text)
        return doc
    
    def apply_lemmatization_model(self, word):
        lemmatized_word = lemmatizeWord(word)
        return lemmatized_word