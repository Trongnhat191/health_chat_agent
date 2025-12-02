import sys
sys.path.append("/home/nhat/Documents/HUST/project 1")

from dataclasses import dataclass
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from dotenv import load_dotenv

from embed.query import query_recipe

load_dotenv()
import os

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