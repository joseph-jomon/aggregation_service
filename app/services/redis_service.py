import redis.asyncio as aioredis
import json
from app.config.config_loader import REDIS_HOST, REDIS_PORT, REDIS_DB

# Create a connection pool for aioredis
redis_client = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}", decode_responses=True)

async def save_embeddings_batch(batch_embeddings: list):
    """
    Asynchronously saves a batch of embedding data into Redis and checks readiness using set operations.

    Args:
        batch_embeddings (list): A list of dictionaries, each containing 'id', 'embedding_type', and 'embedding'.

    Returns:
        list: A list of combined data dictionaries if both embeddings are ready.
    """
    combined_data_list = []

    # Redis set keys to track text and image embeddings readiness
    TEXT_EMBEDDING_SET = "text_embedding_ids"
    IMAGE_EMBEDDING_SET = "image_embedding_ids"

    async with redis_client.pipeline() as pipe:
        for embedding_data in batch_embeddings:
            data_id = embedding_data.id
            embedding_type = embedding_data.embedding_type
            embedding = embedding_data.embedding
            key = f"{data_id}"

            # Store embedding in Redis hash
            existing_data = await redis_client.hgetall(key)
            existing_data[embedding_type] = json.dumps(embedding)
            
            # Add the data to the Redis pipeline
            pipe.hset(key, mapping=existing_data)

            # Add the ID to the appropriate set
            if embedding_type == "EMBEDDINGS_TEXT":
                pipe.sadd(TEXT_EMBEDDING_SET, data_id)
            elif embedding_type == "EMBEDDINGS_IMAGE":
                pipe.sadd(IMAGE_EMBEDDING_SET, data_id)

        # Execute all commands in the pipeline
        await pipe.execute()

    # Use Redis set intersection to find IDs that have both embeddings
    ready_ids = await redis_client.sinter(TEXT_EMBEDDING_SET, IMAGE_EMBEDDING_SET)

    # Retrieve the data for all IDs that are ready using a pipeline
    async with redis_client.pipeline() as pipe:
        for data_id in ready_ids:
            pipe.hgetall(data_id)

        combined_data_list = await pipe.execute()

    # Return only the complete data for ingestion
    return [data for data in combined_data_list if data]
