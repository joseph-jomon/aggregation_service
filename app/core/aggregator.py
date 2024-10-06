from app.services.redis_service import save_embeddings_batch
from app.services.ingestion_service import ingest_combined_data_bulk
import logging

logging.basicConfig(level=logging.INFO)

class Aggregator:
    async def aggregate_data_batch(self, batch_embeddings: list):
        """
        Aggregates a batch of embeddings by checking readiness using Redis set operations.

        Args:
            batch_embeddings (list): A list of embedding data dictionaries.
        """
        # Save embeddings and get combined data that is ready
        combined_data_list = await save_embeddings_batch(batch_embeddings)

        # Ingest the data in bulk if any data is ready
        if combined_data_list:
            logging.info(f"Ingesting {len(combined_data_list)} items to Elasticsearch.")
            await ingest_combined_data_bulk(combined_data_list)
