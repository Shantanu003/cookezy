from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text, create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.sql import *
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from predict import create_recipe
# from sanjivkapoor_scraper import scrape_sanjeev




Base = declarative_base()

app = Flask(__name__)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
cors = CORS(app, resources={r"/*": {"origins": "*"}})
cors = CORS(app)

app.config['JWT_SECRET_KEY'] = 'cookeazyansjsdahdja123123nasd1212'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Shantanu_.003@localhost/cookeazy_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def connect_db():
    #_load_db_vars()
    # create db create_engine
    db = create_engine('mysql://root:Shantanu_.003@localhost/cookeazy_db')
    return db



db=connect_db() #establish connection
Session = sessionmaker(bind=db)
session = Session()



class Ingredient(Base):
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(120), nullable=False)

    ingredients = relationship('Ingredient', backref='user', lazy=True)

    def get_token(self, expires_delta=None):
        return create_access_token(identity=self.id, expires_delta=expires_delta)

class SavedRecipe(Base):
    __tablename__ = 'saved_recipes'

    id = Column(Integer, primary_key=True)
    recipe = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship('User', backref='saved_recipes', lazy=True)


engine = connect_db()
User.__table__.create(bind=engine, checkfirst=True)
Ingredient.__table__.create(bind=engine, checkfirst=True)
SavedRecipe.__table__.create(bind=engine, checkfirst=True)




def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # print(request.headers)
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[0]

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = session.query(User).filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/register', methods=['POST'])
def register():
    
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    # data = request.get_json()
    # print(data)
    user = session.query(User).filter_by(username = username).first()
    if user:
        return jsonify({'error': 'Username already exists.'}), 400
    
    user = session.query(User).filter_by(email = email).first()
    if user:
        return jsonify({'error': 'Email already exists.'}), 400
    
    hashed_password = generate_password_hash(password, method='sha256')

    new_user = User(username = username, email = email, password = hashed_password)

    session.add(new_user)
    session.commit()

    return jsonify({'message': 'User registered successfully'})


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # db fetch
    user = session.query(User).filter_by(username = username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid username or password'}), 401
    # Generate JWT token
    payload = {
        'user_id': str(user.id),
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token})




@app.route('/api/users/ingredients', methods=['GET'])
@token_required
def get_user_ingredients(user):
    # user = session.query(User).(user_id)
    ingredients = session.query(Ingredient).filter_by(user_id=user.id).all()
    result_lst = []
    for ingredient in ingredients:    
        result_dict = {
            "name" : ingredient.name, 
            "unit" : ingredient.unit, 
            "quantity": ingredient.quantity}
        result_lst.append(result_dict)
    
    return jsonify(result_lst) 



@app.route('/api/users/ingredients', methods=['POST'])
@token_required
def add_ingredient(user):
    name = request.json['name']
    quantity = request.json['quantity']
    unit = request.json['unit']

    user = session.query(User).filter_by(id=user.id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    ingredient = Ingredient(name=name.capitalize(), quantity=quantity, unit=unit, user_id=user.id)

    session.add(ingredient)
    session.commit()

    return jsonify({'message': 'Ingredient added successfully'}), 201


@app.route('/api/users/ingredients/<string:name>', methods=['PUT'])
@token_required
def update_ingredient(user, name):
    # get the user and ingredient
    # user = User.query.get(user_id)
    ingredient = session.query(Ingredient).filter_by(name=name.capitalize(), user_id=user.id).first()

    # check if the ingredient exists and belongs to the user
    if not ingredient:
        return jsonify({'error': 'Ingredient not found'}), 404

    # update the ingredient data from the request
    ingredient_data = request.json
    ingredient.name = ingredient_data['name']
    ingredient.quantity = ingredient_data['quantity']
    ingredient.unit = ingredient_data['unit']

    # save the changes to the database
    session.commit()

    return jsonify({'message': 'Ingredient updated successfully'})

@app.route('/api/users/ingredients/<string:ingredient_name>', methods=['DELETE'])
@token_required
def delete_ingredient(user, ingredient_name):
    # First, check if the ingredient exists and belongs to the user
    ingredient = session.query(Ingredient).filter_by(name=ingredient_name, user_id=user.id).first()
    if not ingredient:
        return jsonify({'error': 'Ingredient not found or does not belong to this user'}), 404

    # Delete the ingredient
    session.delete(ingredient)
    session.commit()

    # Return a success response
    return jsonify({'message': 'Ingredient deleted successfully'}), 200

@app.route('/api/users/used_ingredients', methods=['POST'])
@token_required
def get_used_ingredients(user):

    name = request.json['name']
    quantity = request.json['quantity']
    unit = request.json['unit']


    THRESHOLD_VALUE = {
    "number" : 5,
    "grams" : 500,
    "ml" : 300,
    # Add more units and thresholds here
    }

    user = session.query(User).filter_by(id=user.id).first()

    ingredient = session.query(Ingredient).filter_by(name=name.capitalize(), user_id=user.id).first()

    print(ingredient.quantity, quantity)
    rem_quantity = int(ingredient.quantity) - int(quantity)

    if rem_quantity < THRESHOLD_VALUE[unit]:
        message = f"Your remaining {name} quantity is below {THRESHOLD_VALUE[unit]} {unit}. Please restock soon!"

        ingredient = session.query(Ingredient).filter_by(user_id=user.id, name=name.capitalize()).first()
        ingredient.quantity = rem_quantity

        session.commit()

    else:
        ingredient = session.query(Ingredient).filter_by(user_id=user.id, name=name).first()
        ingredient.quantity = rem_quantity

        session.commit()

        message = f"Successfully updated {name} quantity."

    # Return message in JSON format
    return jsonify({'message': message})



@app.route('/api/users/get_saved_recipes', methods=['GET'])
@token_required
def get_saved_recipes(user):
    # Logic to fetch and return saved recipes for the logged-in user from the database
    user = session.query(User).filter_by(id=user.id).first()

    saved_recipes = session.query(SavedRecipe).filter_by(user_id=user.id).all()
    serialized_recipes = []
    for recipe in saved_recipes:
        serialized_recipes.append({
            'id': recipe.id,
            'recipe': recipe.recipe
        })
    
    return jsonify(serialized_recipes)


@app.route('/api/users/save_recipe', methods=['POST'])
@token_required
def save_recipe(user):
    # Logic to save a recipe to the database
    # Access recipe data from the request JSON payload
    recipe_data = request.json
    recipe = recipe_data['recipe']

    user = session.query(User).filter_by(id=user.id).first()

    # Create a new SavedRecipe instance associated with the user and save it to the database
    new_recipe = SavedRecipe(recipe=recipe, user_id=user.id)
    session.add(new_recipe)
    session.commit()


    return jsonify({'message': 'Recipe saved successfully'})

@app.route('/api/users/delete_saved_recipe/<recipe_id>', methods=['DELETE'])
@token_required
def delete_saved_recipe(user, recipe_id):
    # Logic to delete a saved recipe from the database
    user = session.query(User).filter_by(id=user.id).first() 

    recipe = session.query(SavedRecipe).filter_by(id=recipe_id, user_id=user.id).first()
    if not recipe:
        return jsonify({'error': 'Recipe not found or unauthorized'})

    session.delete(recipe)
    session.commit()

    return jsonify({'message': 'Recipe deleted successfully'})

# @app.route('/api/add_user', methods=['POST'])
# def add_user():
#     email = request.json['email']
#     password = request.json['password']
    
#     # Check if user with email already exists
#     user = session.query(User).filter_by(email=email).first()
#     if user:
#         return jsonify({'error': 'User with email already exists.'})

#     # Create new user
#     new_user = User(email=email, password=password)
#     # new_user.set_password(password)
#     session.add(new_user)
#     session.commit()

#     # Issue a JWT for the user "added newly"
#     access_token = new_user.get_token()
    
#     return jsonify({'message': 'User added successfully.', 'access_token': access_token})

# @app.route('/api/users/<int:user_id>', methods=['PUT'])
# def update_user(user_id):
#     user = session.query(User).get(user_id)

#     if not user:
#         return jsonify({'message': 'User not found'}), 404

#     # get the request data
#     data = request.get_json()

#     # update user data
#     user.email = data['email']
#     user.password = data['password']

#     try:
#         session.commit()
#         return jsonify({'message': 'User updated successfully'}), 200
#     except:
#         session.rollback()
#         return jsonify({'message': 'Failed to update user'}), 500
#     finally:
#         session.close()

# @app.route('/api/users/<int:user_id>', methods=['DELETE'])
# def delete_user(user_id):
#     user = session.query(User).get(user_id)
#     if not user:
#         return jsonify({'message': 'User not found.'}), 404

#     session.delete(user)
#     session.commit()
#     return jsonify({'message': 'User deleted successfully.'}), 200



@app.route('/generate-recipes', methods=['POST'])
def generate_recipes():
    data = request.json.get('ingredients')
    data = ", ".join(data)
    return jsonify({"Recipies":create_recipe(data)}),200


from sanjivkapoor_scraper import scrape_sanjeev, scrape_sanjeev_recipe
from archanaskitchen_scrapper import scrape_archanas, scrape_archanas_recipe

@app.route('/quick_links',methods=['POST'])
def get_scraping():
    ingredients = request.json.get('ingredients')
    ingredients = ",".join(ingredients)
    # ret = scrape_sanjeev(ingredients)
    ret = scrape_archanas(ingredients)
    return jsonify({"Status":"success","result":ret})


@app.route('/get_scrapped_recipes',methods=['POST'])
def get_scraped_recipe():
    ingredients = request.json.get('ingredients')
    ingredients = ",".join(ingredients)
    ret = scrape_sanjeev(ingredients)
    op = []
    op.append(scrape_sanjeev_recipe(ret[0]))
    op.append(scrape_sanjeev_recipe(ret[1]))
    op.append(scrape_sanjeev_recipe(ret[2]))
    

    return jsonify({"Status":"success","result":op})




if __name__ == "__main__":
    app.run(debug=True)