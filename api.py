# Author: Aniketh S Deshpande
# API-name: Login
# Flask-Server
# Database: MongoDB

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/quiz"
api = Api(app)
mongo = PyMongo(app)


# SIGNUP-API
class SignUp(Resource):

    # checkAvailability is a function that checks if the email_id
    # can be used to create a new account
    def checkAvailability(self, obj):
        mongo_obj = list(mongo.db.login.find({'email_id': obj['email_id']}))
        if len(mongo_obj)>0:
            return False
        else:
            return True

    # POST: adding new user to the database if checkAvailability returns TRUE
    def post(self):
        obj = request.get_json(force=True)

        if self.checkAvailability(obj) == True:
           mongo.db.login.insert({
               'username': obj['username'],
               'email_id': obj['email_id'],
               'password': obj['password']
           })
           return {'msg': 'Welcome {}!'.format(obj['username'])}
        
        else:
            return {'error': 'email_id: {} already used'.format(obj['email_id'])}

    
# LOGIN-API
class Login(Resource):

    # authenticate is a function that authenticates the username and password

    def authenticate(self, obj):
        mongo_obj = list(mongo.db.login.find({'email_id': obj['email_id']}))
        if len(mongo_obj)>0:
            return False
        else:
            return True

    # POST: adding new user to the database if checkAvailability returns TRUE
    def post(self):
        obj = request.get_json(force=True)

        if self.authenticate(obj) == True:
           mongo.db.login.insert({
               'username': obj['username'],
               'email_id': obj['email_id'],
               'password': obj['password']
           })
           return {'msg': 'Welcome {}!'.format(obj['username'])}
        
        else:
            return {'error': 'email_id: {} already used'.format(obj['email_id'])}



    

# Tables-API

class T_entries(Resource):
    def get(self):
        t_array = []
        for item in mongo.db.t.find():
            t_array.append([item['number'],  int(item['size']), int(item['occupancy']) ])
        return {'table': t_array}
    
    def post(self):
        obj = request.get_json(force=True)
        mongo.db.t.insert(obj)
        return {'object_posted': str(obj)}

    def update(self):
        obj = request.get_json(force=True)
        number, new_size, new_occupancy = obj['number'], obj['new_size'], obj['new_occupancy']
        mongo.db.t.update({'number': number}, {'$set':{'occupancy': new_occupancy}})
        return {'object_updated': str(obj)}
        
    def delete(self):
        obj = request.get_json(force=True)
        name = obj['name']
        mongo.db.q.delete({'name': name})
        return {'object_deleted': str(obj)}

'''
class getQ(Resource):
    # we intend to get the groups that end up in Queue
    def get(self):
        result = bestFit(tables, table_size, group, group_size)
'''        
# resources routing
api.add_resource(SignUp, '/sign_up')
api.add_resource(T_entries, '/t_entries')

if __name__ == '__main__':
    app.run(debug=True, host='192.168.43.27')
