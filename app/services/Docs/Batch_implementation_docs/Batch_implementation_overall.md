Thank you for sharing the current implementation. I'll provide you with modifications to handle the embeddings **in batches** instead of individually, focusing on optimizing both the processing of **Redis operations** and **ingestion to Elasticsearch**.

The key changes involve:
- Processing the embeddings as **batches** in the aggregation service.
- Using **Redis pipelines** to improve performance by reducing round trips.
- Performing **bulk operations** for checking and updating the embeddings in Redis and ingesting data into Elasticsearch.

I'll modify each part accordingly.

### 1. Updated Endpoint to Handle Batch Processing

Currently, the endpoint iterates over each embedding and calls the `aggregate_data` method. I’ll modify it to work with the entire batch at once.

**Updated `routes.py`**:

```python
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
```

### 2. Updated Aggregator to Work with Batches

I'll modify the `Aggregator` class to handle the embeddings as a **batch** instead of individual elements.

**Updated `aggregator.py`**:

```python
from app.services.redis_service import save_embeddings_batch
from app.services.ingestion_service import ingest_combined_data
import logging

logging.basicConfig(level=logging.INFO)

class Aggregator:
    async def aggregate_data_batch(self, batch_embeddings: list):
        """
        Aggregates a batch of embeddings.

        Args:
            batch_embeddings (list): A list of embedding data dictionaries.
        """
        # Use save_embeddings_batch to store and check readiness for the entire batch
        combined_data_list = await save_embeddings_batch(batch_embeddings)

        # Ingest the combined data if both embeddings are ready
        for combined_data in combined_data_list:
            if combined_data:
                logging.info(f"Both embeddings ready for ID: {combined_data['id']}. Sending to ingestion.")
                await ingest_combined_data(combined_data)
```

- **`aggregate_data_batch`** is the new method that handles the embeddings in **batches**.
- Instead of processing one embedding at a time, it uses `save_embeddings_batch` to process the entire batch.

### 3. Updated `save_embedding` to `save_embeddings_batch` for Batch Processing

Now, I'll modify the function that interacts with Redis to leverage **Redis pipelines** for batch operations, which will be more efficient.

**Updated `redis_service.py`**:

```python
import redis.asyncio as aioredis
import json
from app.config.config_loader import REDIS_HOST, REDIS_PORT, REDIS_DB

# Create a connection pool for aioredis
redis_client = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}", decode_responses=True)

async def save_embeddings_batch(batch_embeddings: list):
    """
    Asynchronously saves a batch of embedding data into Redis and checks if both embeddings are ready.

    Args:
        batch_embeddings (list): A list of dictionaries, each containing 'id', 'embedding_type', and 'embedding'.

    Returns:
        list: A list of combined data dictionaries if both embeddings are ready, else None.
    """
    combined_data_list = []

    # Use Redis pipeline to batch operations
    async with redis_client.pipeline() as pipe:
        for embedding_data in batch_embeddings:
            data_id = embedding_data.id
            embedding_type = embedding_data.embedding_type
            embedding = embedding_data.embedding
            key = f"{data_id}"

            # Retrieve existing data for the given ID from Redis
            pipe.hgetall(key)
        
        existing_data_list = await pipe.execute()

        # Use pipeline again to update the batch data in Redis
        async with redis_client.pipeline() as pipe:
            for idx, embedding_data in enumerate(batch_embeddings):
                data_id = embedding_data.id
                embedding_type = embedding_data.embedding_type
                embedding = embedding_data.embedding
                key = f"{data_id}"

                # Update the existing data with the new embedding
                existing_data = existing_data_list[idx]
                existing_data[embedding_type] = json.dumps(embedding)

                # Store the updated data back into Redis
                pipe.hset(key, mapping=existing_data)

                # Check if both embeddings are ready
                if 'EMBEDDINGS_TEXT' in existing_data and 'EMBEDDINGS_IMAGE' in existing_data:
                    combined_data_list.append(existing_data)
                else:
                    combined_data_list.append(None)

            # Execute all the set operations in one go
            await pipe.execute()

    return combined_data_list
```

**Key Changes**:
- **Batch Retrieval and Update**:
  - The **first pipeline** retrieves the current state of all hashes for the batch of embeddings.
  - The **second pipeline** updates each hash with the new embedding data.
- **Batch Check for Both Embeddings**:
  - After updating, the function checks whether both text and image embeddings are available, and only then adds them to the list of combined data.

### 4. Ingestion Service

The ingestion service does not need changes because it already takes a dictionary of combined data. However, we could consider modifying it to handle **bulk ingestion** if multiple embeddings are ready at once, improving performance even further.

**Bulk Ingestion Example (Optional)**:
```python
import httpx

async def ingest_combined_data_bulk(data_list: list):
    """
    Ingests a batch of combined data into the database.

    Args:
        data_list (list): A list of combined data dictionaries.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post("http://database-service:8000/ingest/{index_name}", json=data_list)
        return response.status_code, response.json()
```

If you want to use **bulk ingestion**, you could modify `aggregate_data_batch` to collect all ready data and send them as a list to `ingest_combined_data_bulk`.

### Summary of Modifications

1. **Endpoint (`routes.py`)**:
   - Modified to pass the entire batch to the aggregator instead of looping through each item.

2. **Aggregator (`aggregator.py`)**:
   - Modified to handle a batch of embeddings using `aggregate_data_batch`.
   - Collects ready embeddings for ingestion in bulk.

3. **Redis Service (`redis_service.py`)**:
   - Modified to use **Redis pipelines** for batch retrieval and updating of embedding data.
   - This ensures more efficient I/O operations and minimizes network round trips.

4. **Optional Bulk Ingestion**:
   - Added an optional bulk ingestion method for **Elasticsearch**, which can be used to send multiple combined embeddings at once, further improving efficiency.

These changes will make the **aggregation service** more efficient, utilizing batch processing to reduce the number of network round trips and taking advantage of **bulk operations** for better performance, aligning with best practices for professional data pipelines.