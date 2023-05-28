from flask import Flask
from flask_restful import Resource, Api
from flask import request,Response
from flask_cors import CORS
import json
import requests
# from dotenv import load_dotenv
import os

# load_dotenv()


class searchRecipe(Resource):

    ingredient_list = ["onion", "tomato", "potato", "garlic"]

    def searchRecipe(self,ingredient_list):
        response = request.post(os.link)
        print(response)
        return response

    def post(self):
        try:
            data = request.get_json()
            form_data = {
                "kitchen": data['ingredients'],
                "needsimage": 1,
                "app": 1,
                "fave": False,
                "lang":"en",
                "cv":2
            }
            print("inside try")
            response = requests.post(os.getenv("ENDPOINT"), data=form_data)
            res= response.json()
            results = res['results']
            return results[0:10]
        except Exception as error:
            print(error)