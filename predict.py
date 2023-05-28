import threading
import time
from transformers import pipeline

pl = pipeline(task='text-generation',model='./CookGPT')


def create_prompt(ingredients):
    ingredients = ','.join([x.strip().lower() for x in ingredients.split(',')])
    ingredients = ingredients.strip().replace(',','\n')
    s = f"<|startoftext|>Ingredients:\n{ingredients}\n"
    return s

import numpy as np
import random


# print(ingredients1)

# print(len(ingredients1))

# for j in range(4) : 
#   for i in range(len(ingredients1)-1,0,-1):
#     if ingredients1[i] == ",":
#       ingredients1=ingredients1[0:i]
#       break
#   print(ingredients1) 
#   ingredients.append(ingredients1)


#   print(tmplst)



def create_multiple(ingredients):
    ing = []
    # ingredients1 = ' '.join([map(str(),ingredients.split(","))])
    # ingredients1 = ingredients1.split(",")
    for i in range(1):
      tmplst = ingredients.copy()
      # print(tmplst)
      indx = random.randint(0,len(ingredients)-1)
      tmplst.pop(indx)
      tmplst = ",".join(tmplst.copy())
      ing.append(tmplst)
    
    return create_multiple_recipies(ing)

def create_multiple_recipies(ingredients):
    recipes = []
    print("generating recipies")

    for ing in ingredients:
        prompt = create_prompt(ing)
        op = pl(prompt,
             max_new_tokens=512,
             penalty_alpha=0.6,
             top_k=4,
             pad_token_id=50259
            )[0]['generated_text']
        print(op)
        
        # write_to_file(op)
        recipes.append(op)
    return recipes






