import weaviate
from glob import glob
from FlagEmbedding import BGEM3FlagModel

def get_file_path_list():
    file_list = glob('data/recipe_txt_data/*.txt')
    return file_list

def read_content_from_file(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

        split_contents = content.split('++++++++++++')

        ingredients = split_contents[0]
        instructions = split_contents[1]

    return ingredients, instructions

if __name__ == "__main__":
    client = weaviate.connect_to_local()

    model = BGEM3FlagModel('BAAI/bge-m3',  
                        use_fp16=True)
    try:
        recipes = client.collections.get("Recipes")
        file_list = get_file_path_list()
        for file in file_list:
            ingredients, instructions = read_content_from_file(file)
            print("===================================")
            print("Start embedding File:", file)
            name = file.split('/')[-1].replace('.txt', '')
            # print("Ingredients:", ingredients)
            # print("Instructions:", instructions)
            
            embedded_ingredients = model.encode(ingredients)["dense_vecs"]
            embedded_instructions = model.encode(instructions)["dense_vecs"]

            for section in ['instructions', 'ingredients']:
                if section == 'instructions':
                    text = instructions
                    embedding = {"dense_vecs": embedded_instructions}
                else:
                    text = ingredients
                    embedding = {"dense_vecs": embedded_ingredients}
                recipes.data.insert(
                    {
                        "title": name,
                        "content": text,
                        "section": section
                    },
                    vector=embedding["dense_vecs"]
                )

    finally:
        client.close()
