from FlagEmbedding import BGEM3FlagModel
import weaviate

model = BGEM3FlagModel('BAAI/bge-m3',  
                        use_fp16=True)
client = weaviate.connect_to_local()

recipes = client.collections.get("Recipes")

def query_recipe(query: str, top_k: int = 3):
    query_vec = model.encode(query)["dense_vecs"]
    results = recipes.query.near_vector(near_vector=query_vec.tolist(), 
                                        limit=top_k,
                                        return_metadata=["distance", "certainty"])
    return results

if __name__ == "__main__":
    query = "Bánh cuốn là gì?"
    results = query_recipe(query, top_k=3)
    for r in results.objects:
        print(f"Title: {r.properties['title']}")
        print(f"Section: {r.properties['section']}")
        print(f"Content: {r.properties['content']}")
        print(f"Distance: {r.metadata.distance}")
        print(f"Certainty: {r.metadata.certainty}")
        print("===================================")