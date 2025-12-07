import gradio as gr
import sys
import os
# sys.path.append("/home/nhat/Documents/HUST/project 1")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from agent.agent import agent, UserContext

def ask_agent(question, history):
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        context=UserContext(user_id="user123")
    )
    return result['messages'][-1].content

iface = gr.ChatInterface(
    fn=ask_agent,
    # inputs=gr.Textbox(label="Nhập câu hỏi về ẩm thực"),
    # outputs=gr.Markdown(label="Trả lời"),
    title="Trợ lý Ẩm thực",
    description="Đặt câu hỏi về công thức nấu ăn hoặc phép tính."
)

if __name__ == "__main__":
    iface.launch()