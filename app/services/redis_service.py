import aioredis
import json
from app.config import REDIS_HOST, REDIS_PORT, REDIS_DB

# Create a connection pool for aioredis
redis_client = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}", decode_responses=True)

async def save_embedding(data_id: str, data: dict, embedding_type: str):
    """
    Asynchronously saves the embedding data into Redis and checks if both embeddings are ready.

    Args:
        data_id (str): The unique identifier for the data.
        data (dict): The embedding data to be stored.
        embedding_type (str): The type of embedding (either text or image).
    
    Returns:
        dict: The complete data if both embeddings are ready, else None.
    """
    # Use Redis to store the data asynchronously
    key = f"{data_id}"

    # Retrieve existing data for the given ID from Redis
    existing_data = await redis_client.hgetall(key)

    # Update the data with the new embedding (either text or image)
    existing_data[embedding_type] = json.dumps(data)

    # Store the updated data back into Redis
    await redis_client.hset(key, mapping=existing_data)

    # Check if both embeddings are ready
    if 'EMBEDDINGS_TEXT' in existing_data and 'EMBEDDINGS_IMAGE' in existing_data:
        # If both are present, return the complete data to be processed for ingestion
        return existing_data

    # If both embeddings are not yet available, return None
    return None
