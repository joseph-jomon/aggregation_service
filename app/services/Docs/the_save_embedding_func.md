The check for determining whether both embeddings (`EMBEDDINGS_TEXT` and `EMBEDDINGS_IMAGE`) are available for a given ID takes place within the `save_embedding()` function in the **`app/services/redis_service.py`** file. Here’s the relevant section of the code explained in detail:

```python
def save_embedding(data_id: str, data: dict, embedding_type: str):
    # Use Redis to store the data
    key = f"{data_id}"
    
    # Retrieve existing data for the given ID from Redis
    existing_data = redis_client.hgetall(key)
    
    # Update the data with the new embedding (either text or image)
    existing_data[embedding_type] = data
    
    # Store the updated data back into Redis
    redis_client.hmset(key, existing_data)

    # Check if both embeddings are ready
    if 'EMBEDDINGS_TEXT' in existing_data and 'EMBEDDINGS_IMAGE' in existing_data:
        # If both are present, return the complete data to be processed for ingestion
        return existing_data
    
    # If both embeddings are not yet available, return None
    return None
```

### Breakdown of the Check in `save_embedding()`:

1. **Store/Update Data in Redis**:
   - The function `save_embedding()` is called whenever a text or image embedding is received.
   - It uses the `data_id` to uniquely identify the corresponding record in Redis.
   - The `existing_data` dictionary is updated to include the new embedding (either text or image) using the embedding type (`embedding_type`, which is either `"EMBEDDINGS_TEXT"` or `"EMBEDDINGS_IMAGE"`).

2. **Checking for Both Embeddings**:
   - After updating the `existing_data` dictionary, the function performs a check to see if **both** embeddings (`EMBEDDINGS_TEXT` and `EMBEDDINGS_IMAGE`) are present for that `data_id`.
   - Specifically, this check is done with:
     ```python
     if 'EMBEDDINGS_TEXT' in existing_data and 'EMBEDDINGS_IMAGE' in existing_data:
     ```
   - If **both** embeddings are found in the `existing_data` dictionary, this means that the data is now complete (both text and image embeddings are available for the given `id`).

3. **Returning Complete Data**:
   - If the condition above is satisfied, the function returns the complete data (`existing_data`) for further processing.
   - If **both** embeddings are **not** available yet (e.g., only text or only image), the function returns `None`, which indicates that the aggregation process should wait until the missing embedding is available.

4. **Aggregation Layer Usage**:
   - In the **`app/core/aggregator.py`** file, the returned value from `save_embedding()` is checked:
     ```python
     if data:
         # If `data` is not None, it means both embeddings are available
         await ingest_combined_data(data)
     ```
   - This ensures that the ingestion service is called only when the data for a given `id` is fully aggregated (i.e., both text and image embeddings are present).

### Summary
The check takes place in the `save_embedding()` function where Redis is used to store each embedding and track completeness. The check is to see if both `EMBEDDINGS_TEXT` and `EMBEDDINGS_IMAGE` exist in Redis for a given `data_id`. Only when both are present does the function return the complete data, allowing it to be ingested by the database service.