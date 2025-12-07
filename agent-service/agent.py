import sys
import os
# sys.path.append("/home/nhat/Documents/HUST/project 1")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dataclasses import dataclass
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from dotenv import load_dotenv

load_dotenv()
import os

def connect_weaviate():
    from FlagEmbedding import BGEM3FlagModel
    import weaviate

    model = BGEM3FlagModel('BAAI/bge-m3',  
                            use_fp16=True)
    client = weaviate.connect_to_custom(
        http_host = "weaviate",
        http_port= 8080,
        http_secure= False,
        grpc_host= "weaviate",
        grpc_port = 50051,
        grpc_secure= False
    )

    recipes = client.collections.get("Recipes")
    return model, recipes

def query_recipe(query: str, top_k: int = 3):
    model, recipes = connect_weaviate()
    query_vec = model.encode(query)["dense_vecs"]
    results = recipes.query.near_vector(near_vector=query_vec.tolist(), 
                                        limit=top_k,
                                        return_metadata=["distance", "certainty"])
    return results

@dataclass
class UserContext:
    user_id: str

@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers and returns the product"""
    return a * b

@tool
def search_recipes(query: str, top_k: int = 1) -> str:
    """
    Tìm kiếm công thức nấu ăn trong cơ sở dữ liệu.
    
    Args:
        query: Câu hỏi hoặc từ khóa tìm kiếm về món ăn, công thức
        top_k: Số lượng kết quả trả về (mặc định là 3)
    
    Returns:
        Thông tin về các công thức nấu ăn liên quan
    """
    results = query_recipe(query, top_k=top_k)
    
    if not results.objects:
        return "Không tìm thấy công thức nào phù hợp."
    
    output = []
    for i, r in enumerate(results.objects, 1):
        output.append(f"""
                        **Kết quả {i}:**
                        - Tiêu đề: {r.properties.get('title', 'N/A')}
                        - Phần: {r.properties.get('section', 'N/A')}
                        - Nội dung: {r.properties.get('content', 'N/A')}
                        - Độ tương đồng: {r.metadata.certainty:.2%}
                        """)
    
    return "\n".join(output)



model = ChatGroq(model="openai/gpt-oss-120b", 
                 api_key=os.getenv("GROQ_API"),
                   temperature=0,
                     streaming=True)
agent = create_agent(
    model,
    tools=[multiply, search_recipes],
    context_schema=UserContext,
    system_prompt="Bạn là trợ lý ẩm thực thông minh. Bạn có thể tìm kiếm công thức nấu ăn và thực hiện các phép tính. Hãy trả lời bằng tiếng Việt."
)

if __name__ == "__main__":
        result = agent.invoke(
        {"messages": [{"role": "user", "content": "Thành phần nguyên liệu của phở gà là gì?"}]},
        context=UserContext(user_id="user123")
        )
        # print(result)
        print("AI Response:", result['messages'][-1].content)
        print('----------------------------')
        # print(result['messages'][1].additional_kwargs['tool_calls'])
        # print(result['messages'][1].additional_kwargs['tool_calls'][0]['function'])
        # print("Tool Name:", result['messages'][1].additional_kwargs['tool_calls'][0]['function']['name'])