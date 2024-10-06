from app.services.redis_service import save_embedding
from app.services.ingestion_service import ingest_combined_data

class Aggregator:
    async def aggregate_data(self, data_id: str, embedding_type: str, embedding: list):
         # Save embedding and check if both text and image embeddings are ready
        data = save_embedding(data_id, {"id": data_id, embedding_type: embedding}, embedding_type)
        if data:
            # Send the combined data to ingestion once both embeddings are ready
            await ingest_combined_data(data)
