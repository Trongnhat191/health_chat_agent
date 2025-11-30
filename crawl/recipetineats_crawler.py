import requests
from bs4 import BeautifulSoup as bs
import os
from utils.save_crawled_file import save_to_file

def get_article_link(soup): # Lấy link bài viết từ trang danh mục
    article_link_list = []

    articles_html = soup.find_all('article', class_ = 'category-vietnamese-recipes')
    for article in articles_html:
        name_link_pair = {}
        # print('----------')
        name = article.text.strip()
        # print(name)
        link = article.find('a').get('href')
        # print('..........')
        # print(link)
        name_link_pair[name] = link
        article_link_list.append(name_link_pair)

    return article_link_list

def get_content_html(link): # Lấy content html từ link bài viết
    article = requests.get(link)
    article_soup = bs(article.text, 'html.parser')
    content_html = article_soup.find_all('div', class_ = 'wprm-entry-content')

    return content_html

def get_ingredients(link): # Lấy phần nguyên liệu từ bài viết
    content_html = get_content_html(link)
    ingredients_html = content_html[0].find_all('li', class_ = 'wprm-recipe-ingredient')
    ingredients = ''

    for ingredient in ingredients_html:
        ingredient_text = ingredient.text[1:].strip()
        ingredient_text += '\n'
        ingredients += ingredient_text
    return ingredients

def get_instructions_html(link): # Lấy phần hướng dẫn nấu từ bài viết
    content_html = get_content_html(link)
    instructions_html = content_html[0].find_all('div', class_ = 'wprm-recipe-instruction-text')
    instructions = ''

    for instruction in instructions_html:
        instruction_text = instruction.text.strip()
        instruction_text += '\n'
        instructions += instruction_text
    return instructions

if __name__ == '__main__':
    response = requests.get('https://www.recipetineats.com/category/vietnamese-recipes/')
    soup = bs(response.text, 'html.parser')

    article_link_list = get_article_link(soup)
    for article_link in article_link_list:
        for name, link in article_link.items():
            results_text = ''
            try:
                ingredients = get_ingredients(link)
                # print(ingredients)
                instructions = get_instructions_html(link)
                # print(instructions)
                results_text = 'Ingredients of ' + name + ':\n' + ingredients + '++++++++++++\nInstructions of ' + name + ':\n' + instructions
                save_to_file(name, results_text)
            except Exception as e:
                print(f"Error processing {name}: {e}")
                continue


                       
            