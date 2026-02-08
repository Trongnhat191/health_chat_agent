import sys
sys.path.append("/home/nhat/Documents/HUST/project 1")

from dataclasses import dataclass
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.tools import tool
from dotenv import load_dotenv
import requests
from FlagEmbedding import BGEM3FlagModel
import weaviate
import os
from langgraph.checkpoint.memory import InMemorySaver  

load_dotenv()

API_KEY = os.getenv("USDA_KEY")
BASE_URL = os.getenv("NUTRITION_API_URL")
YOLO_API_URL = os.getenv("YOLO_API_URL")
GROQ_API_KEY = os.getenv("GROQ_API")
MODEL_NAME = os.getenv("MODEL_NAME")
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "localhost")
WEAVIATE_PORT = int(os.getenv("WEAVIATE_PORT", 8080))
WEAVIATE_GRPC_PORT = int(os.getenv("WEAVIATE_GRPC_PORT", 50051))

model = BGEM3FlagModel('BAAI/bge-m3',  
                        use_fp16=True, cache_dir= "./model")
# client = weaviate.connect_to_local()
client = weaviate.connect_to_custom(
    http_host=WEAVIATE_URL,
    http_port=WEAVIATE_PORT,
    http_secure=False,
    grpc_host=WEAVIATE_URL,
    grpc_port=WEAVIATE_GRPC_PORT,
    grpc_secure=False,
)
recipes = client.collections.get("Recipes")

def query_recipe(query: str, top_k: int = 3):
    query_vec = model.encode(query)["dense_vecs"]
    results = recipes.query.near_vector(near_vector=query_vec.tolist(), 
                                        limit=top_k,
                                        return_metadata=["distance", "certainty"])
    return results

@dataclass
class UserContext:
    user_id: str

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
    print(f'Gọi tool tìm kiếm công thức với truy vấn')
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

@tool
def search_nutrition(food: str) -> str:
    """
    Tìm kiếm thông tin dinh dưỡng của một loại thực phẩm bằng tiếng anh
    
    Args:
        food: Tên loại thực phẩm cần tìm kiếm
    
    Returns:
        Thông tin dinh dưỡng của thực phẩm
    """
    if not API_KEY:
        return "Lỗi: API key không được cấu hình (USDA_KEY)."
    print(f'Gọi tool tìm kiếm dinh dưỡng')
    # Tìm fdcId của thực phẩm
    url = f"{BASE_URL}/foods/search"
    params = {
        "query": food,
        "pageSize": 1,
        "api_key": API_KEY
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    print(data)

    if "foods" not in data or not data["foods"]:
        return "Không tìm thấy thực phẩm nào."

    first_food = data["foods"][0]
    fdc_id = first_food["fdcId"]

    # Lấy thông tin dinh dưỡng chi tiết từ fdcId
    url = f"{BASE_URL}/food/{fdc_id}"
    params = {"api_key": API_KEY}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    # Build output string (trả về thay vì print)
    out_lines = []
    out_lines.append(f"Thông tin dinh dưỡng cho: {data.get('description','N/A')}\n")
    out_lines.append("{:<35} {:>10} {:>10}".format("Chất dinh dưỡng", "Lượng", "Đơn vị"))
    out_lines.append("-" * 60)

    for nutrient in data.get("foodNutrients", []):
        if nutrient.get("amount") <= 0:
            continue
        name = nutrient.get("nutrient", {}).get("name", "N/A")
        amount = nutrient.get("amount", 0) or 0
        unit = nutrient.get("nutrient", {}).get("unitName", "")
        out_lines.append("{:<35} {:>10.2f} {:>10}".format(name, amount, unit))
    print("\n".join(out_lines))
    print('-----------------------------')
    return "\n".join(out_lines)

@tool
def detect_recipe_from_image(image_path: str):
    """
    Nhận diện món ăn hoặc nguyên liệu từ hình ảnh bằng cách gửi tới YOLO service.
    
    Args:
        image_path: Đường dẫn tuyệt đối tới file ảnh cần nhận diện.
    
    Returns:
        Danh sách các nhãn (labels) nhận diện được từ ảnh.
    """
    url = YOLO_API_URL
    print(f'Gọi tool nhận diện ảnh tại')
    if not os.path.exists(image_path):
        return f"Lỗi: Không tìm thấy file ảnh tại {image_path}"

    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            # Gửi ảnh tới API YOLO
            response = requests.post(url, files=files)
            
        if response.status_code == 200:
            data = response.json()
            labels = data.get("labels", [])
            if labels:
                # Lọc trùng lặp
                unique_labels = list(set(labels))
                return f"Hệ thống nhận diện được các thành phần trong ảnh: {', '.join(unique_labels)}"
            else:
                return "Hệ thống không nhận diện được đối tượng nào rõ ràng trong ảnh."
        else:
            return f"Lỗi từ dịch vụ nhận diện ảnh: {response.status_code}"
    except Exception as e:
        return f"Lỗi khi kết nối tới dịch vụ nhận diện ảnh: {str(e)}"

model_agent = ChatGroq(model=MODEL_NAME,
                 api_key=GROQ_API_KEY,
                   temperature=0,
                     streaming=False)
agent = create_agent(
    model_agent,
    tools=[search_recipes, search_nutrition, detect_recipe_from_image],
    checkpointer=InMemorySaver(), 
    context_schema=UserContext,
    # system_prompt="Bạn là trợ lý ẩm thực thông minh. Bạn có thể tìm kiếm công thức nấu ăn và thực hiện các phép tính. Hãy trả lời bằng tiếng Việt.")
    system_prompt="""Bạn là trợ lý ẩm thực thông minh, thân thiện. 
- Nếu người dùng hỏi các câu xã giao hoặc kiến thức chung không cần tra cứu, hãy trả lời trực tiếp.
- Chỉ sử dụng công cụ khi cần tìm kiếm dữ liệu cụ thể về công thức, dinh dưỡng hoặc hình ảnh.
- Trả lời bằng tiếng Việt lịch sự.""")

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