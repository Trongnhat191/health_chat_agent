import requests
from bs4 import BeautifulSoup as bs

modern_url = 'https://bunbobae.com/category/recipes/vietnamese-recipes/modern-vietnamese/' 
response = requests.get(modern_url)

soup = bs(response.text, 'html.parser')

recipe_index_html = soup.find_all('div', class_ = 'feast-recipe-index')

modern_recipes_html = recipe_index_html[0]#có 2 class feast-recipe-index tìm được nhưng chỉ dùng cái đầu, cái sau là gợi ý món khác

modern_recipes_html_lst = modern_recipes_html.find_all("li", class_ = 'listing-item')

modern_recipes_link_list = []
for li in modern_recipes_html_lst:
    modern_recipes_link_list.append(li.find('a').get('href'))