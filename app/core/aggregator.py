from app.services.redis_service import save_embedding
from app.services.ingestion_service import ingest_combined_data
import logging
logging.basicConfig(level=logging.INFO)

class Aggregator:
    async def aggregate_data(self, data_id: str, embedding_type: str, embedding: list):
        # Save embedding and check if both text and image embeddings are ready
        logging.info(f"Aggregating data for ID: {data_id}, Type: {embedding_type}")
        data = await save_embedding(data_id, {"id": data_id, embedding_type: embedding}, embedding_type)
        if data:
            logging.info(f"Both embeddings ready for ID: {data_id}. Sending to ingestion.")
            # Send the combined data to ingestion once both embeddings are ready
            await ingest_combined_data(data)
