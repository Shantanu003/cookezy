import threading
import time
import os
from transformers import pipeline

current_directory = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(current_directory, 'CookEzzy\CookGPT')

pl = pipeline(task='text-generation',model=model_path)


def create_prompt(ingredients):
    ingredients = ','.join([x.strip().lower() for x in ingredients.split(',')])
    ingredients = ingredients.strip().replace(',','\n')
    s = f"<|startoftext|>Ingredients:\n{ingredients}\n"
    return s

import numpy as np
import random


def create_recipe(ingredients):
    recipes = []
    print(ingredients)
    
    # print("generating recipes")

    # for ing in ingredients:
    prompt = create_prompt(ingredients)
    op = pl(prompt,
         max_new_tokens=512,
         penalty_alpha=0.6,
         top_k=4,
         pad_token_id=50259
        )[0]['generated_text']
    # print(op)

    return op






