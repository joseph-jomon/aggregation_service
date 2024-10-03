from fastapi import APIRouter
from app.core.aggregator import Aggregator

router = APIRouter()
aggregator = Aggregator()

@router.post("/aggregate/")
async def send_for_aggregation(data: dict):
    embedding_type = data.get("embedding_type")
    data_id = data.get("id")
    embedding = data.get("embedding")

    if not (embedding_type and data_id and embedding):
        return {"status": "Invalid request"}

    # Aggregate data in Redis
    aggregator.aggregate_data(data_id, embedding_type, embedding)
    return {"status": "Data sent for aggregation."}
