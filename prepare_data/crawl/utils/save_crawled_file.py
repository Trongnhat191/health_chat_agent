import os 

def save_to_file(name, ingredients):
    os.makedirs("data/recipe_txt_data", exist_ok=True)
    file_name = os.path.join('data', "recipe_txt_data", name + '.txt')

    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(ingredients)