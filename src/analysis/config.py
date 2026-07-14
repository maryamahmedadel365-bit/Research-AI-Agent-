import os

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint


def get_llm():
    endpoint = HuggingFaceEndpoint(
        repo_id=os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3"),
        huggingfacehub_api_token=os.getenv("HF_TOKEN"),
        task="text-generation",
    )
    return ChatHuggingFace(llm=endpoint)
