import gradio as gr
import sys
sys.path.append("/home/nhat/Documents/HUST/project 1")
from agent.agent import agent, UserContext

def ask_agent(message, history):
    # Khi multimodal=True, message là dict: {'text': str, 'files': list}
    question = message["text"]
    files = message.get("files", [])
    
    # Nếu người dùng upload ảnh, ta thêm chỉ dẫn vào prompt để Agent biết dùng tool
    if files:
        image_path = files[0]
        print(image_path)
        question += f"\n\n[System: Người dùng đã tải lên một bức ảnh tại đường dẫn: {image_path}. Hãy sử dụng công cụ 'detect_recipe_from_image' để phân tích bức ảnh này trước khi trả lời.]"

    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        context=UserContext(user_id="user123")
    )
    return result['messages'][-1].content

iface = gr.ChatInterface(
    fn=ask_agent,
    title="Trợ lý Ẩm thực",
    multimodal=True,
    description="Đặt câu hỏi về công thức nấu ăn hoặc phép tính."
)

if __name__ == "__main__":
    iface.launch()