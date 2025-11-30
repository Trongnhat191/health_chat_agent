from weaviate.classes.config import Property, DataType, Configure
import weaviate
def create_schema(schema_name: str):
    client = weaviate.connect_to_local()
    try:
        recipes = client.collections.create(
            name=schema_name,
            properties=[
                Property(name="title", data_type=DataType.TEXT),
                Property(name="content", data_type=DataType.TEXT),
                Property(name="section", data_type=DataType.TEXT),
            ],
            # vector_config=Configure.Vectorizer.none(),  # Nếu bạn tự embedding
        )
        print(f"Schema '{schema_name}' created successfully.")
    finally:
        client.close()

if __name__ == "__main__":
    create_schema("Recipes")

