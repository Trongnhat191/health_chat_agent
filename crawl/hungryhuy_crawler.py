import requests
from bs4 import BeautifulSoup as bs
from utils.save_crawled_file import save_to_file

def get_article_link(soup): # Lấy link bài viết từ trang danh mục
    article_link_list = []

    articles_html = soup.find_all('section', class_ = 'posts-grid')
    dishes_html = articles_html[0].find_all('h2', class_ = 'entry-title')

    for dish in dishes_html:
        name_link_pair = {}
        # print('----------')
        name = dish.text.strip()
        # print(name)
        link = dish.find('a').get('href')
        # print(link)
        name_link_pair[name] = link
        article_link_list.append(name_link_pair)
    return article_link_list

def get_ingredients_and_instructions(link): # Lấy phần nguyên liệu từ bài viết
    article = requests.get(link)
    article_soup = bs(article.text, 'html.parser')
    ingredients_and_instructions_html = article_soup.find_all('div', class_ = 'wprm-recipe-template-cutout-hungry-huy-container')
    
    
    ingredients = ''
    for ingredient in ingredients_and_instructions_html[0].find_all('li', class_ = 'wprm-recipe-ingredient'):
        ingredient_text = ingredient.text[1:].strip()
        ingredient_text += '\n'
        ingredients += ingredient_text
        # print(ingredient_text)
        # print('..............')
    # print(ingredients)

    instructions = ''
    for instruction in ingredients_and_instructions_html[0].find_all('div', class_ = 'wprm-recipe-instruction-text'):
        instruction_text = instruction.text.strip()
        instruction_text += '\n'
        instructions += instruction_text
        # print(instruction_text)
        # print('..............')
    # print(instructions)
    return ingredients, instructions

if __name__ == '__main__':
    response = requests.get('https://www.hungryhuy.com/vietnamese/main-dishes-vietnamese/')
    soup = bs(response.text, 'html.parser')

    article_link_list = get_article_link(soup)
    
    for article_link in article_link_list:
        for name, link in article_link.items():
            results_text = ''
            try:
                ingredients, instructions = get_ingredients_and_instructions(link)
                name = name.replace('/', '_')
                print(name)
                print(ingredients)
                # instructions = get_instructions_html(link)
                print(instructions)
                print('-------------------')
                results_text = 'Ingredients of ' + name + ':\n' + ingredients + '++++++++++++\nInstructions of ' + name + ':\n' + instructions + '-----------------\n'
                save_to_file(name, results_text)
            except Exception as e:
                print(f"Error processing {name}: {e}")
                continue
