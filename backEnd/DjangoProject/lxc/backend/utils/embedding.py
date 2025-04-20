import dashscope
import numpy as np
from django.conf import settings

dashscope.api_key = settings.DASHSCOPE_API_KEY

def get_embedding(text: str) -> np.ndarray:
    rsp = dashscope.TextEmbedding.call(
        model="text-embedding-v1",
        input=text,
    )
    if rsp.status_code == 200:
        return np.array(rsp.output.embeddings[0])
    else:
        raise Exception(f"Embedding API failed: {rsp.message}")
