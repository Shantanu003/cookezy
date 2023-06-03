import time
import requests
from bs4 import BeautifulSoup
import urllib.parse


def scrape_recipe_websites(ing):
    query = ing + " site:www.archanaskitchen.com"
    qry = urllib.parse.quote(query)

    google_str = "https://www.google.com/search?q="+qry
    response_g = requests.get(google_str)

    soup = BeautifulSoup(response_g.content, 'html.parser')
    name = soup.find_all('a')

    name = name[16:28]
    urls = []

    for n in name:
        n = str(n).split("q=")
        n = n[1].split("&amp")
        urls.append(n[0])

    return list(set(urls))

def scrape_archanas_recipe(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    name = soup.find('h1', class_='recipe-title')

    recipe_ingredients = soup.find('div', class_='recipeingredients')
    ingredients_li_elements = recipe_ingredients.find_all('li', itemprop='ingredients')

    recipe_instructions =  soup.find('div', class_='recipeinstructions')
    instructions_li_elements = recipe_instructions.find_all('li', itemprop='recipeInstructions')
    
    # recipe_image_div = soup.find('div', class_='recipe-image')
    # img_element = recipe_image_div.find('img')
    # image_url = "https://www.archanaskitchen.com" + soup.find('img',class_="recipe-image")['src']
    # print(image_url)

    name =  name.text.strip()
    ingredients = []
    instructions = []

    for ele in ingredients_li_elements :
        ingredient = ele.text.strip()
        ingredients.append(ingredient)

    for li in instructions_li_elements:
        instruction = li.text.strip()
        instructions.append(instruction)

    ret = {
        "name":name,
        "ingredients":ingredients,
        "instruction":instructions,
        # "image_url":image_url
    }

    return ret


