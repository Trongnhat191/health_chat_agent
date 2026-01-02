from fastapi import FastAPI, HTTPException, UploadFile, File, Form
import shutil
import os
import uuid
from typing import Optional

app = FastAPI(title="Agent Service")

# --- LAZY LOADING (Quan trọng) ---
# Biến toàn cục để lưu agent, ban đầu để None
_agent = None
_UserContext = None

def get_agent():
    """
    Hàm này chỉ import và khởi tạo agent khi có request đầu tiên gọi đến.
    Giúp container khởi động nhanh, không bị crash nếu Weaviate chưa sẵn sàng lúc boot.
    """
    global _agent, _UserContext
    if _agent is None:
        print("Đang khởi tạo Agent và kết nối Weaviate/Model lần đầu...")
        try:
            from agent import agent as imported_agent, UserContext as imported_context
            _agent = imported_agent
            _UserContext = imported_context
            print("Khởi tạo Agent thành công!")
        except Exception as e:
            print(f"Lỗi khởi tạo Agent: {e}")
            raise e
    return _agent, _UserContext

@app.post("/chat")
async def chat(
    message: str = Form(...), 
    user_id: str = Form("default_user"),
    file: Optional[UploadFile] = File(None)
):
    try:
        # 1. Lấy agent (Lazy load)
        agent_instance, context_class = get_agent()

        # 2. Xử lý file ảnh nếu có
        image_context = ""
        if file:
            # Tạo thư mục tạm
            temp_dir = "/tmp/agent_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Lưu file
            file_ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(temp_dir, filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Báo cho Agent biết đường dẫn ảnh
            # Agent sẽ dùng tool 'detect_recipe_from_image' với đường dẫn này
            image_context = f"\n[System: Người dùng gửi kèm ảnh tại: {file_path}]"

        # 3. Gọi Agent
        full_message = message + image_context
        
        result = agent_instance.invoke(
            {"messages": [{"role": "user", "content": full_message}]},
            context=context_class(user_id=user_id)
        )
        
        return {"response": result['messages'][-1].content}

    except Exception as e:
        # In lỗi ra logs để debug
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))