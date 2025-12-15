import sys
sys.path.append("/home/nhat/Documents/HUST/project 1")

from dataclasses import dataclass
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from dotenv import load_dotenv
import requests

from embed.query import query_recipe

load_dotenv()
import os

API_KEY = os.getenv("USDA_KEY")
BASE_URL = "https://api.nal.usda.gov/fdc/v1"

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
    # URL của YOLO service (chạy trên docker map ra localhost:8000)
    url = "http://localhost:8000/predict"
    
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

model = ChatGroq(model="openai/gpt-oss-120b", 
                 api_key=os.getenv("GROQ_API"),
                   temperature=0,
                     streaming=True)
agent = create_agent(
    model,
    tools=[search_recipes, search_nutrition, detect_recipe_from_image],
    context_schema=UserContext,
    system_prompt="Bạn là trợ lý ẩm thực thông minh. Bạn có thể tìm kiếm công thức nấu ăn và thực hiện các phép tính. Hãy trả lời bằng tiếng Việt.")
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