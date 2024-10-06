from pydantic import BaseModel
from typing import List

class Embedding(BaseModel):
    id: str
    embedding_type: str  # Can be "EMBEDDINGS_TEXT" or "EMBEDDINGS_IMAGE"
    embedding: List[float]

class BatchEmbeddings(BaseModel):
    embeddings: List[Embedding]
