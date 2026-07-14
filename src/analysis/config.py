import os

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint


def get_llm():
    endpoint = HuggingFaceEndpoint(  # type: ignore
        repo_id=os.getenv("HF_MODEL", "Qwen/Qwen2.5-72B-Instruct"),
        huggingfacehub_api_token=os.getenv("HF_TOKEN"),
        task="text-generation",
    )
    return ChatHuggingFace(llm=endpoint)

