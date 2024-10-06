Yes, that's correct. Since you've updated **`save_embedding`** to be an **asynchronous function** using `aioredis`, it **must be awaited** when called inside **`aggregate_data`**. This ensures that the embedding is properly saved in Redis before proceeding to the next steps.

Here’s the corrected version of the **`Aggregator`** class:

### Updated `Aggregator` Class:

```python
import logging
from app.services.redis_service import save_embedding
from app.services.ingestion_service import ingest_combined_data

class Aggregator:
    async def aggregate_data(self, data_id: str, embedding_type: str, embedding: list):
        # Save embedding and check if both text and image embeddings are ready
        logging.info(f"Aggregating data for ID: {data_id}, Type: {embedding_type}")
        
        # Correctly await the save_embedding function since it is now async
        data = await save_embedding(data_id, {"id": data_id, embedding_type: embedding}, embedding_type)
        
        if data:
            logging.info(f"Both embeddings ready for ID: {data_id}. Sending to ingestion.")
            # Send the combined data to ingestion once both embeddings are ready
            await ingest_combined_data(data)
```

### Key Changes:

1. **Await `save_embedding`**:
   - The **`save_embedding`** function is now an **async function**, which means it needs to be awaited when called:
   ```python
   data = await save_embedding(data_id, {"id": data_id, embedding_type: embedding}, embedding_type)
   ```
   - This ensures the async function runs correctly and returns its result after completing the Redis operation.

2. **Reason for Awaiting**:
   - Without **`await`**, the `save_embedding` function would return a coroutine object, and the Redis operation wouldn't be executed as expected.
   - **`await`** is necessary for the function to complete the I/O operation (saving the embedding in Redis) before moving forward.

### Summary:

- Updating **`save_embedding`** to use **`aioredis`** and making it **async** means you **must await** this function wherever it's called.
- The **`await`** keyword is crucial to ensure that the Redis operation completes properly before continuing to the next steps, such as checking if both embeddings are ready and proceeding with ingestion.
- This change aligns well with the async architecture and ensures that each I/O operation is non-blocking and properly awaited, improving the concurrency and responsiveness of the application.