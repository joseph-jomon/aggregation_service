import redis
from app.config import REDIS_HOST, REDIS_PORT, REDIS_DB

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

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