import time
import requests
from bs4 import BeautifulSoup
import urllib.parse


def scrape_recipes(ing):
    query = ing + " site:sanjeevkapoor.com"
    qry = urllib.parse.quote(query)

    google_str = "https://www.google.com/search?q="+qry
    response_g = requests.get(google_str)

    soup = BeautifulSoup(response_g.content, 'html.parser')
    name = soup.find_all('a')

    name = name[16:25]
    urls = []
    for n in name:
        n = str(n).split("/url?q=")
        n = n[1].split("&amp")
        urls.append(n[0])

    return list(set(urls))
 

def scrape_sanjeev_recipe(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    name = soup.find('h1', class_='dancef spcemrgin')
    recipe_ingredients = soup.find('div', class_='ingredientlist')
    ingredients_li_elements = recipe_ingredients.find_all('span', itemprop='ingredients')
    recipe_instructions = soup.find('div', class_='methodlist')

    instructions_li_elements = recipe_instructions.find_all('div', class_='stepdetail')
    
    image_url = "https://www.sanjeevkapoor.com" + soup.find('img',class_="recipimg")['src']
    # print(image_url)

    name =  name.text.strip().replace("Card","")
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
        "image_url":image_url
    }

    return ret


