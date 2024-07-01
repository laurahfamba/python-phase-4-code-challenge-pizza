from models import Restaurant, RestaurantPizza, Pizza
from app import app, db
from faker import Faker

class TestApp:
    """Unit tests for Flask application in app.py"""

    fake = Faker()

    def setup_method(self):
        """Setup method to create initial data before each test."""
        with app.app_context():
            db.create_all()

    def teardown_method(self):
        """Teardown method to clean up after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_restaurants(self):
        """Retrieves restaurants with GET request to /restaurants"""
        with app.app_context():
            restaurant1 = Restaurant(name=self.fake.name(), address=self.fake.address())
            restaurant2 = Restaurant(name=self.fake.name(), address=self.fake.address())
            db.session.add_all([restaurant1, restaurant2])
            db.session.commit()

            response = app.test_client().get('/restaurants')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            response = response.json
            assert [restaurant['id'] for restaurant in response] == [restaurant.id for restaurant in Restaurant.query.all()]
            assert [restaurant['name'] for restaurant in response] == [restaurant.name for restaurant in Restaurant.query.all()]
            assert [restaurant['address'] for restaurant in response] == [restaurant.address for restaurant in Restaurant.query.all()]
            for restaurant in response:
                assert 'restaurant_pizzas' not in restaurant

    def test_restaurants_id(self):
        """Retrieves one restaurant using its ID with GET request to /restaurants/<int:id>"""
        with app.app_context():
            restaurant = Restaurant(name=self.fake.name(), address=self.fake.address())
            db.session.add(restaurant)
            db.session.commit()

            response = app.test_client().get(f'/restaurants/{restaurant.id}')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            response = response.json
            assert response['id'] == restaurant.id
            assert response['name'] == restaurant.name
            assert response['address'] == restaurant.address
            assert 'restaurant_pizzas' in response

    def test_returns_404_if_no_restaurant_to_get(self):
        """Returns an error message and 404 status code with GET request to /restaurants/<int:id> by a non-existent ID"""
        with app.app_context():
            response = app.test_client().get('/restaurants/0')
            assert response.status_code == 404
            assert response.content_type == 'application/json'
            assert response.json.get('error') == "Restaurant not found"

    def test_deletes_restaurant_by_id(self):
        """Deletes restaurant with DELETE request to /restaurants/<int:id>"""
        with app.app_context():
            restaurant = Restaurant(name=self.fake.name(), address=self.fake.address())
            db.session.add(restaurant)
            db.session.commit()

            response = app.test_client().delete(f'/restaurants/{restaurant.id}')
            assert response.status_code == 204

            result = Restaurant.query.filter_by(id=restaurant.id).first()
            assert result is None

    def test_returns_404_if_no_restaurant_to_delete(self):
        """Returns an error message and 404 status code with DELETE request to /restaurants/<int:id> by a non-existent ID"""
        with app.app_context():
            response = app.test_client().delete('/restaurants/0')
            assert response.status_code == 404
            assert response.content_type == 'application/json'
            assert response.json.get('error') == "Restaurant not found"

    def test_pizzas(self):
        """Retrieves pizzas with GET request to /pizzas"""
        with app.app_context():
            pizza1 = Pizza(name=self.fake.name(), ingredients=self.fake.sentence())
            pizza2 = Pizza(name=self.fake.name(), ingredients=self.fake.sentence())
            db.session.add_all([pizza1, pizza2])
            db.session.commit()

            response = app.test_client().get('/pizzas')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            response = response.json

            pizzas = Pizza.query.all()

            assert [pizza['id'] for pizza in response] == [pizza.id for pizza in pizzas]
            assert [pizza['name'] for pizza in response] == [pizza.name for pizza in pizzas]
            assert [pizza['ingredients'] for pizza in response] == [pizza.ingredients for pizza in pizzas]
            for pizza in response:
                assert 'restaurant_pizzas' not in pizza

    def test_creates_restaurant_pizzas(self):
        """Creates one restaurant_pizzas using a pizza_id, restaurant_id, and price with a POST request to /restaurant_pizzas"""
        with app.app_context():
            pizza = Pizza(name=self.fake.name(), ingredients=self.fake.sentence())
            restaurant = Restaurant(name=self.fake.name(), address=self.fake.address())
            db.session.add(pizza)
            db.session.add(restaurant)
            db.session.commit()

            response = app.test_client().post('/restaurant_pizzas',
                                             json={
                                                 "price": 3,
                                                 "pizza_id": pizza.id,
                                                 "restaurant_id": restaurant.id,
                                             }
                                             )

            assert response.status_code == 201
            assert response.content_type == 'application/json'
            response = response.json
            assert response['price'] == 3
            assert response['pizza_id'] == pizza.id
            assert response['restaurant_id'] == restaurant.id
            assert response['id']
            assert response['pizza']
            assert response['restaurant']

            query_result = RestaurantPizza.query.filter_by(restaurant_id=restaurant.id, pizza_id=pizza.id).first()
            assert query_result.price == 3

    def test_400_for_validation_error(self):
        """Returns a 400 status code and error message if a POST request to /restaurant_pizzas fails"""
        with app.app_context():
            pizza = Pizza(name=self.fake.name(), ingredients=self.fake.sentence())
            restaurant = Restaurant(name=self.fake.name(), address=self.fake.address())
            db.session.add(pizza)
            db.session.add(restaurant)
            db.session.commit()

            response = app.test_client().post('/restaurant_pizzas',
                                             json={
                                                 "price": 0,  # Invalid price
                                                 "pizza_id": pizza.id,
                                                 "restaurant_id": restaurant.id,
                                             }
                                             )

            assert response.status_code == 400
            assert response.json['errors'] == ["validation errors"]

            response = app.test_client().post('/restaurant_pizzas',
                                             json={
                                                 "price": 31,  # Invalid price
                                                 "pizza_id": pizza.id,
                                                 "restaurant_id": restaurant.id,
                                             }
                                             )

            assert response.status_code == 400
            assert response.json['errors'] == ["validation errors"]
