import os

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "huggingface")  # "huggingface" | "openai"


def get_llm():
    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)

    from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

    endpoint = HuggingFaceEndpoint(
        repo_id=os.environ.get("HF_MODEL", "Qwen/Qwen2.5-72B-Instruct"),
        huggingfacehub_api_token=os.environ["HUGGINGFACEHUB_API_TOKEN"],
        temperature=0.01,  # HF endpoint requires > 0, not exactly 0
        max_new_tokens=1024,
    )
    return ChatHuggingFace(llm=endpoint)