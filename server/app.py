#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os
from sqlalchemy import desc



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
        response = make_response([{'address':restaurant.address,'id':restaurant.id,'name':restaurant.name} for restaurant in Restaurant.query.all()], 200)
        return response

class IndividualRestaurant(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id = id).first()
        if restaurant:

            json_response = {
                'address': restaurant.address,
                'id': restaurant.id,
                'name': restaurant.name,
                'restaurant_pizzas': [
                    {
                        'id': rp.id,
                        'pizza_id': rp.pizza_id,  # Include pizza_id
                        'price': rp.price,  # Include price
                        'restaurant_id': rp.restaurant_id,  # Include restaurant_id
                        'pizza': {
                            'id': rp.pizza.id,
                            'name': rp.pizza.name,
                            'ingredients': rp.pizza.ingredients
                        }
                    } for rp in restaurant.restaurant_pizzas
                ]
            }
            response  = make_response(json_response, 200)
            return response
        else:
            return ({'error': "Restaurant not found"}, 404)

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id = id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return {}, 204
        else:
            return {"error": "Restaurant not found"}, 404
        
class Pizzas(Resource):
    def get(self):
        response = make_response([{'id':pizza.id,'ingredients':pizza.ingredients,'name':pizza.name} for pizza in Pizza.query.all()], 200)
        return response
    
class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_pizza = RestaurantPizza(price = data['price'], pizza_id = data['pizza_id'], restaurant_id = data['restaurant_id'])
            print(new_pizza.to_dict())
            if new_pizza:
                
                db.session.add(new_pizza)
                db.session.commit()

                restaurant_pizza_object = RestaurantPizza.query.order_by(desc(RestaurantPizza.id)).first()
                response_item = {
                        "id": restaurant_pizza_object.id,
                        "pizza_id": restaurant_pizza_object.pizza_id,
                        "price": restaurant_pizza_object.price,
                        "restaurant_id": restaurant_pizza_object.restaurant_id,
                        "pizza" : restaurant_pizza_object.pizza.to_dict(),
                        "restaurant": restaurant_pizza_object.restaurant.to_dict()
                }
                print(restaurant_pizza_object.to_dict())
                return  response_item, 201
            else:
                return {'errors': '[validation errors]'}, 404
        except ValueError as e:
            response = make_response({"errors": ['validation errors']}, 400)
            return response

api.add_resource(Home, '/home')
api.add_resource(Restaurants, '/restaurants')
api.add_resource(IndividualRestaurant, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')
if __name__ == "__main__":
    app.run(port=5555, debug=True)