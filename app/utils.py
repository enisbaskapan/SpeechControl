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
    
    def format_weekdays(self, weekday_index):
        #weekdays = [self.weekday_list.index(weekday) for weekday in entities['weekdays']]
        weekdays = [(self.today + datetime.timedelta((index-self.today.weekday()) % 7)) for index in weekday_index]
        return weekdays
    
    def format_delays(self, delay):
        dates = [(self.today + datetime.timedelta(weeks=1)) for d in delay]
        return dates
    
    def format_sdelays(self, sdelay, compare=False):
        #delay tagleri içerisinde geçen kelimeye göre hafta veya gün sonrasını alma
        dates = []
        for sd in sdelay:
            if 'hafta' in sd[1]:
                sdelay_count = datetime.timedelta(weeks=int(sd[0]))
                dates.append(sdelay_count)
            if 'gün' in sd[1]:
                sdelay_count = datetime.timedelta(days=int(sd[0]))
                dates.append(sdelay_count)
        
        if compare==False:
            for index, date in enumerate(dates):
                dates[index] = self.today + date
            return dates
                
        return sdelay_count
    
    def format_datetime(self, date):
        
        current_year = datetime.date.today().year
        formatted_date = datetime.datetime(current_year, month_list.index(str(date[1])) + 1, int(date[0]))
        return formatted_date
    
    def format_dates(self, dates):
        
        formatted_dates = [self.format_datetime(date) for date in dates]
        
        if len(formatted_dates)==2 and formatted_dates[0] > formatted_dates[1]: 
            formatted_dates[1] = formatted_dates[1] + datetime.timedelta(days=365)
                
        return formatted_dates

class Compare(Format):
    
    def __init__(self):
        
        super().__init__()

    def compare_dates(self, response_content):
        date0 = response_content['date0']
        date1 = response_content['date1']
        if date0 != "" and date1 != "":
            if date0 < date1:
                temp_date = date0
                date0 = date0
                date1 = temp_date
                
        if date0 != "": date0 = self.format_date_string(date0)
        if date1 != "": date1 = self.format_date_string(date1)

        response_content['date0'] = date0
        response_content['date1'] = date1
        
        return response_content
            
    def compare_weekdays(self, weekdays):
        
        weekdays = self.format_weekdays(weekdays)
   
        if len(weekdays) == 2 and weekdays[1] < weekdays[0]:
            weekdays[1] = weekdays[1] + datetime.timedelta(weeks=1)
      
        return weekdays
    
    def compare_delays(self, delays, sdelays):
        if len(delays)==1 and len(sdelays)==1:
            delay = delays[0]
            sdelay = sdelays[0]
            # Compare delay indexes Example: delay = ('haftaya',2) sdelay = (2,'gün sonraya',3)
            #                                                   ^            ^               ^
            #                                                 index     sdelay amount      index
            if delay[1] < sdelay[2]:
                date0 = self.format_delays(delay)
                date1 = date0 + self.format_sdelay(sdelay, compare=True)             
            else:
                date0 = self.today + self.format_sdelay(sdelay, compare=True)
                date1 = self.today + self.format_delays(delay)

class Process(Compare):
    
    def __init__(self):
        
        super().__init__()
    
    def process_dates(self, dates, weekdays):
        
        if len(dates)==2:
            self.response_content['date0'] = dates[0]
            self.response_content['date1'] = dates[1]
        elif len(dates)==1 and len(weekdays)==0:
            self.response_content['date0'] = dates[0]
        elif len(dates)==1 and len(weekdays)==1:
            self.response_content['date0'] = weekdays[0]
            self.response_content['date1'] = dates[1]
        elif len(weekdays)==2:
            self.response_content['date0'] = weekdays[0]
            self.response_content['date1'] = weekdays[1]    
        else:
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            tomorrow = self.format_date_string(tomorrow)
            self.response_content['date0'] = tomorrow
        return self.response_content
    
    def process_delays(self, delays, sdelays):

        if len(delays)==2:
            self.response_content['date0'] = delays[0]
            self.response_content['date1'] = delays[1]
        elif len(delays)==1 and len(sdelays)==0:
            self.response_content['date0'] = delays[0]
        elif len(delays)==0 and len(sdelays)==1:
            self.response_content['date0'] = sdelays[0]
        elif len(delays)==1 and len(sdelays)==1:
            self.response_content['date0'] = delays[0]
            self.response_content['date1'] = sdelays[0]
        elif len(sdelays)==2:
            self.response_content['date0'] = sdelays[0]
            self.response_content['date1'] = sdelays[1]
        
        return self.response_content
    
    def process_stations(self, stations, defaultLocation):
        
        if len(stations) == 2:
            From, To = stations
            self.response_content['from0'] = From
            self.response_content['to0'] = To
            
            self.response_content['from1'] = To
            self.response_content['to1'] = From
            
        elif len(stations) == 1: 
            
            # Assign default_location as the departure location that is retrieved from0 GPS
            From, To = defaultLocation, stations[0]

            self.response_content['from0'] = From
            self.response_content['to0'] = To
            
            self.response_content['from1'] = To
            self.response_content['to1'] = From
            
        elif len(stations) == 0:
            self.response_content['no_stations'] = True
            
        return self.response_content
                    
    def process_passengers(self, passengers):
        
        self.response_content['Passengers'] = passengers
        return self.response_content

    def process_self(self, self_):
        
        if len(self_) != 0:
            self.response_content['Passengers'].append((1, self_[0]))
        return self.response_content
 
    def process_available_stations(self, response_content, response):
        
        if response_content['no_stations']:
            response['exampleArrival']['stationList'] = list(station_vocab.keys())
            
            
        del response_content['no_stations']
        
        if response_content['from0'] == response_content['to0']:
            response['exampleArrival']['stationList'] = list(station_vocab.keys())
            
        return response_content, response
    
    def process_url(self, response):
        if response['exampleArrival']["stationList"] != [""]:
            response['url'] = ""
        return response
    
    def process_datetime(self, dates, weekdays, delays, sdelays):
    
        if len(delays)==1 and len(sdelays)==1: delays, sdelays = self.compare_delays(self, delays, sdelays)

        elif len(sdelays)==0: delays = self.format_delays(delays)

        elif len(delays)==0: sdelays = self.format_sdelays(sdelays)

        if len(dates)!=0: dates = self.format_dates(dates)

        if len(weekdays)==2: weekdays = self.compare_weekdays(weekdays)
        
        if len(weekdays)!=0: weekdays = self.format_weekdays(weekdays)

        return dates, weekdays, delays, sdelays

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

class Obtain:
    
    def obtain_date_indexes(self, months, numbers):
        
        dates = []
        for month in months:
            for number in numbers:
                if month[1]-1==number[1]:
                    dates.append((number[0],month[0]))
                    numbers.remove(number)
                elif month[1]+1==number[1]:
                    dates.append((number[0],month[0]))
                    numbers.remove(number)
                    
        return dates, numbers

    def obtain_passenger_indexes(self, passenger_types, numbers):
        
        passengers = []
        for passenger in passenger_types:
            for number in numbers:
                if passenger[1]-1==number[1]:
                    passengers.append((number[0],passenger[0]))
                    numbers.remove(number)
                else:
                    passengers.append((1,passenger[0]))
        return passengers
    
    def obtain_sdelay_indexes(self, sdelays, numbers):
        
        s_delays = []
        for delay in sdelays:
            for number in numbers:
                if delay[1]-1==number[1]:
                    s_delays.append((number[0],delay[0],delay[1]))
                    numbers.remove(number)
                    
        return s_delays, numbers
    
    def obtain_indexes(self, dates, passengers, sdelays, numbers):
        
        if len(dates) != 0:
            dates, numbers = self.obtain_date_indexes(dates, numbers)
        if len(sdelays) != 0:
            sdelays, numbers = self.obtain_sdelay_indexes(sdelays, numbers)
        if len(passengers) != 0:
            passengers = self.obtain_passenger_indexes(passengers, numbers)
        
        return dates, passengers, sdelays

class Apply:
    
    def apply_ner_model(self, text):
        ner_model = load('app/nlp/model-best')
        doc = ner_model(text)
        return doc
    
    def apply_lemmatization_model(self, word):
        lemmatized_word = lemmatizeWord(word)
        return lemmatized_word