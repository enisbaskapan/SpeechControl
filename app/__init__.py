from flask import Flask
from flask_restplus import Api, fields, Namespace
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class FlaskApp():

	def __init__(self):
		
		self.cache = Cache()
		self.api = Api()
		self.db = SQLAlchemy()

	def register_flask_extensions(self, app):
	    
		self.api.init_app(app)
		self.cache.init_app(app)
		return self.api, self.cache

	def configure_flask_app(self, app):
	    
		app.config['CACHE_TYPE'] = 'simple'
		app.config.from_pyfile('./config/application-'+ app.config['ENV'] +'-properties.py')

	def create_flask_app(self):    
	    
		app = Flask(__name__)
		self.configure_flask_app(app)
		api, cache = self.register_flask_extensions(app)
		return app, api, cache

class CreateApp(FlaskApp):

	def create_swagger_ui(self):

		swagger = Namespace('ner', description = 'Speech Control API')
		url = swagger.model('ner', {"Sentence": fields.String(required=True, description="Enter speech-to-text output")})

		return swagger, url

	def create_app(self):

		swagger, url = self.create_swagger_ui()
		app, api, cache = self.create_flask_app()
		return app, api, cache, self.db, swagger, url

# Start Application
create_app = CreateApp()
app, api, cache, db, swagger, url = create_app.create_app()

# Database Configuration & Integration
#Base = declarative_base() 
#engine = create_engine(app.config['DATABASE_URL'], echo=True)





# Months
# 2 months "İstanbul-Eryaman trenine 3 yetişkin 2 asker 27 Eylül gidiş 2 Ekim dönüş"
# 2 months "İstanbul-Eryaman trenine 3 yetişkin 2 asker 2 Ekim dönüş 27 Eylül gidiş" ? compare_dates bugün ile karşılaştır
# 1 month 1 weekday "Pazartesi gidip 23 Aralık'ta dönen Eskişehir trenine 2 yetişkin İstanbul" 
# 1 month 1 delay "Haftaya gidip 23 Aralık'ta dönen Eskişehir trenine 2 yetişkin İstanbul" 
# 1 month 1 sdelay "2 gün sonra gidip 23 Aralık'ta dönen Eskişehir trenine 2 yetişkin İstanbul" 

# Weekdays
# 2 weekdays "Pazartesi gidip cumartesi dönen Eskişehir trenine 2 yetişkin İstanbul" 
# 1 weekday 1 delay "Yarın gidip cumartesi dönen Eskişehir trenine 2 yetişkin İstanbul" ? compare delay and weekday
# 1 weekday 1 sdelay "2 gün sonra gidip cumartesi dönen Eskişehir trenine 2 yetişkin İstanbul" ? compare sdelay and weekday

# Sdelay
# 2 sdelays "2 gün sonra gidip 5 gün sonraya dönen Eskişehir trenine 2 yetişkin İstanbul" 
# 1 delay 1 sdelay "Haftaya gidip 5 gün sonraya dönen Eskişehir trenine 2 yetişkin İstanbul"

# Delay
# 2 delays "Yarın gidip haftaya dönen Eskişehir trenine 2 yetişkin İstanbul" 


# Bugünün tarihi --> yıl, 06-12-2022
# 27 aralık, 2 ocak
# date0 > date1
# date1 year + 1

# Bugünün tarihi --> yıl
# 2 aralık, 7 aralık
# date0 > date1
# date1 year + 1