import redis
from app.config import REDIS_HOST, REDIS_PORT, REDIS_DB

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def save_embedding(data_id: str, data: dict, embedding_type: str):
    key = f"{data_id}"
    existing_data = redis_client.hgetall(key)
    existing_data[embedding_type] = data
    redis_client.hmset(key, existing_data)

    # Check if both embeddings are ready
    if 'EMBEDDINGS_TEXT' in existing_data and 'EMBEDDINGS_IMAGE' in existing_data:
        return existing_data
    return None
