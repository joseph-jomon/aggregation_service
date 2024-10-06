from fastapi import APIRouter
from app.core.aggregator import Aggregator
from app.models.data_model import BatchEmbeddings

router = APIRouter()
aggregator = Aggregator()

@router.post("/aggregate/", response_model=dict)
async def send_for_aggregation(batch_data: BatchEmbeddings):
    # Pass the entire batch to the aggregator
    await aggregator.aggregate_data_batch(batch_data.embeddings)
    return {"status": "Batch data sent for aggregation."}
