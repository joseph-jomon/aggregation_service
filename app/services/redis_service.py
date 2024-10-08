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
        list: A list of combined data dictionaries that are ready for ingestion, including 'id', 'text_embedding', and 'image_embedding'.
    """
    combined_data_dict = {}

    # Redis set keys to track text and image embeddings readiness
    TEXT_EMBEDDING_SET = "text_embedding_ids"
    IMAGE_EMBEDDING_SET = "image_embedding_ids"

    # Step 1: Store the incoming embeddings in Redis and track their readiness
    async with redis_client.pipeline() as pipe:
        for embedding_data in batch_embeddings:
            data_id = embedding_data.id  # Ensure we use the ID
            embedding_type = embedding_data.embedding_type
            embedding = embedding_data.embedding
            index_name = embedding_data.index_name # Get the index name
            key = f"{data_id}"

            # Retrieve the current data stored for this ID from Redis
            existing_data = await redis_client.hgetall(key)

            # Update the existing data with the new embedding and index_name
            existing_data[embedding_type] = json.dumps(embedding)
            existing_data['index_name'] = index_name # Store index_name with the data 

            # Add the updated data to the Redis pipeline
            pipe.hset(key, mapping=existing_data)

            # Add the ID to the corresponding set for tracking readiness
            if embedding_type == "EMBEDDINGS_TEXT":
                pipe.sadd(TEXT_EMBEDDING_SET, data_id)
            elif embedding_type == "EMBEDDINGS_IMAGE":
                pipe.sadd(IMAGE_EMBEDDING_SET, data_id)

        # Execute all commands in the pipeline
        await pipe.execute()

    # Step 2: Use Redis set intersection to find IDs that have both embeddings
    ready_ids = await redis_client.sinter(TEXT_EMBEDDING_SET, IMAGE_EMBEDDING_SET)

    # Step 3: Retrieve the data for all IDs that are ready using a pipeline
    async with redis_client.pipeline() as pipe:
        for data_id in ready_ids:
            pipe.hgetall(data_id)

        combined_data_list = await pipe.execute()

    # Step 4: Construct the combined data list with IDs and their respective embeddings
    # Format the combined data properly and include the ID and index_name
    formatted_combined_data_list = []
    for data_id, combined_data in zip(ready_ids, combined_data_list):
        if 'EMBEDDINGS_TEXT' in combined_data and 'EMBEDDINGS_IMAGE' in combined_data:
            formatted_combined_data_list.append({
                'id': data_id,
                'text_embedding': json.loads(combined_data['EMBEDDINGS_TEXT']),
                'image_embedding': json.loads(combined_data['EMBEDDINGS_IMAGE']),
                'index_name': combined_data['index_name']  # Include the index name for ingestion
            })

    return formatted_combined_data_list
