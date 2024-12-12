#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class Home(Resource):
    def get(self):
        return "<h1>Code challenge</h1>", 200

class Restaurants(Resource):
    def get(self):
        return [restaurant.to_dict() for restaurant in Restaurant.query.all()], 200
api.add_resource(Home, '/home')
api.add_resource(Restaurants, '/restaurants')
if __name__ == "__main__":
    app.run(port=5555, debug=True)
