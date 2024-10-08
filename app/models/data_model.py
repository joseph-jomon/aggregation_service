from pydantic import BaseModel
from typing import List

class Embedding(BaseModel):
    id: str
    embedding_type: str  # Can be "EMBEDDINGS_TEXT" or "EMBEDDINGS_IMAGE"
    embedding: List[float]
    index_name: str  # Add index name here to identify the company/immobilien service

class BatchEmbeddings(BaseModel):
    embeddings: List[Embedding]
