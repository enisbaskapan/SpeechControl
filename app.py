from flask import request, jsonify
from flask_restplus import Resource, fields, Namespace
from flask_migrate import Migrate

from app import app, api, cache, db, swagger, url
#from app import Base, engine
from app.service import Extract

#Create Tables If Doesn't Exist
#@app.before_first_request
#def create_tables():
	#Base.metadata.create_all(bind = engine)

@cache.cached(timeout = app.config['TIMEOUT'])
@swagger.route("")
@swagger.response(204, 'Parsing is successful...')
class RailwayEntityRecognition(Resource):
        
	@swagger.expect(url)
	def post(self):
		"""
		#
		* Speech Control API receives two inputs; 
		
		* First one is the defaultLocation parameter that is the closest destination to the users location. It is received from the front-end and utilized in case the user don't specify a departure location. 
		
		* Second one is the text input that consists passenger, date and location information. It is later transformed into a link and send back as the response.
        """
		extract = Extract()
		response = extract.extract(request.get_json())
		return jsonify(response)

#Activate Swagger UI
api.add_namespace(swagger) 

#Migration
Migrate(app, db)   

if __name__ == "__main__":
	db.init_app(app)
	app.run(host=app.config['HOST'], port=app.config['PORT'], debug = app.config['DEBUG'])