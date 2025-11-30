import weaviate

def delete_schema(schema_name: str):
    client = weaviate.connect_to_local()
    try:
        client.collections.delete(schema_name)
        print(f"Schema '{schema_name}' deleted successfully.")
    finally:
        client.close()
if __name__ == "__main__":
    delete_schema("Recipes")