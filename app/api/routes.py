from fastapi import APIRouter
from app.core.aggregator import Aggregator
from app.models.data_model import BatchEmbeddings

router = APIRouter()
aggregator = Aggregator()

@router.post("/aggregate/", response_model=dict)
async def send_for_aggregation(batch_data: BatchEmbeddings):
    # Iterate over each embedding in the batch
    for embedding_data in batch_data.embeddings:
        # embedding_data.embedding_type is now correctly defined
        await aggregator.aggregate_data(embedding_data.id, embedding_data.embedding_type, embedding_data.embedding)
    return {"status": "Batch data sent for aggregation."}
