import requests
from bs4 import BeautifulSoup as bs

def get_modern_vietnamese_recipes_links():
    modern_url = 'https://bunbobae.com/category/recipes/vietnamese-recipes/modern-vietnamese/' 
    response = requests.get(modern_url)

    soup = bs(response.text, 'html.parser')

    recipe_index_html = soup('div', class_ = 'feast-recipe-index')

    modern_recipes_html = recipe_index_html[0]#có 2 class feast-recipe-index tìm được nhưng chỉ dùng cái đầu, cái sau là gợi ý món khác

    modern_recipes_html_lst = modern_recipes_html.find_all("li", class_ = 'listing-item')
    modern_recipes_link_list = []
    for li in modern_recipes_html_lst:
        modern_recipes_link_list.append(li.find('a').get('href'))
    return modern_recipes_link_list

if __name__ == '__main__':
    links = get_modern_vietnamese_recipes_links()
    for link in links:
        print(link)
        