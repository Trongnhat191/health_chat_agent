import gradio as gr
import requests
import os

# Lấy URL của Agent API từ biến môi trường
AGENT_API_URL = os.getenv("AGENT_API_URL", "http://localhost:8001/chat")

def ask_agent(message, history):
    # message có thể là dict (multimodal) hoặc str
    files_payload = []
    text_message = ""

    if isinstance(message, dict):
        text_message = message["text"]
        files = message.get("files", [])
        if files:
            # Gradio trả về list đường dẫn file tạm
            # Mở file ở chế độ binary read để gửi đi
            # files[0] là đường dẫn file ảnh
            files_payload = [('file', open(files[0], 'rb'))]
    else:
        text_message = message
    
    # Chuẩn bị payload dạng form data (dùng cho tham số data= của requests)
    payload = {
        "message": text_message,
        "user_id": "user123"
    }

    try:
        # QUAN TRỌNG:
        # - Dùng data=payload để gửi form-data (thay vì json=payload)
        # - Dùng files=files_payload để gửi file
        if files_payload:
            response = requests.post(AGENT_API_URL, data=payload, files=files_payload)
        else:
            response = requests.post(AGENT_API_URL, data=payload)
            
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"Lỗi kết nối tới Agent: {str(e)}"

iface = gr.ChatInterface(
    fn=ask_agent,
    title="Trợ lý Ẩm thực AI",
    multimodal=True,
    description="Đặt câu hỏi về công thức nấu ăn hoặc upload ảnh món ăn."
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)