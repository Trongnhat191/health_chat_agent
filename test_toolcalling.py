from llama_index.llms.groq import Groq
from llama_index.core.agent.workflow import FunctionAgent
from dotenv import load_dotenv
import os
load_dotenv()

GROQ_API = os.getenv("GROQ_API")

def multiply(a: float, b: float) -> float:
    """Multiply two numbers and returns the product"""
    return a * b


def add(a: float, b: float) -> float:
    """Add two numbers and returns the sum"""
    return a + b

llm = Groq(model="openai/gpt-oss-20b", api_key=GROQ_API)

workflow = FunctionAgent(
    tools=[multiply, add],
    llm=llm,
    system_prompt="You are an agent that can perform basic mathematical operations using tools.",
)

async def main():
    response = await workflow.run(user_msg="What is 20+(2*4)?")
    print(response)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())