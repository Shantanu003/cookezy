import time
import requests
from bs4 import BeautifulSoup
import urllib.parse


def scrape_archanas(ing):
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


# url = "https://www.archanaskitchen.com/chicken-in-tomato-onion-gravy-recipe"

# response = requests.get(url)
# soup = BeautifulSoup(response.content, 'html.parser')

# name = soup.find('h1', class_='recipe-title').text.strip()
# print("name : ", name)

# # Find the div element with class 'recipeinstructions'
# recipe_instructions = soup.find('div', class_='recipeinstructions')

# # Find all the li elements within the recipe instructions
# li_elements = recipe_instructions.find_all('li', itemprop='recipeInstructions')

# # Loop through each li element and extract the text within it
# print("instructions : ")
# for li in li_elements:
#     instruction = li.text.strip()
#     print(instruction)

# recipe_ingredients = soup.find('div', class_='recipeingredients')

# # Find all the li elements within the recipe ingredients
# li_elements = recipe_ingredients.find_all('li', itemprop='ingredients')

# # Loop through each li element and extract the ingredient text
# print("Ingredients : ")
# for li in li_elements:
#     ingredient = li.text.strip()
#     print(ingredient)


# # Find the div element with class 'recipe-image'
# recipe_image_div = soup.find('div', class_='recipe-image')

# # Find the img element within the recipe image div
# img_element = recipe_image_div.find('img')

# # Extract the 'src' attribute value from the img element
# image_url = img_element['src']

# print("Image Url : ", image_url)

def scrape_archanas_recipe(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    name = soup.find('h1', class_='recipe-title').text.strip()

    recipe_ingredients = soup.find('div', class_='recipeingredients')
    ingredients_li_elements = recipe_ingredients.find_all('li', itemprop='ingredients')

    recipe_instructions =  soup.find('div', class_='recipeinstructions')
    instructions_li_elements = recipe_instructions.find_all('li', itemprop='recipeInstructions')
    
    # recipe_image_div = soup.find('div', class_='recipe-image')
    # img_element = recipe_image_div.find('img')
    image_url = "https://www.archanaskitchen.com" + soup.find('img',class_="recipe-image")['src']
    # print(image_url)

    name =  name
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


