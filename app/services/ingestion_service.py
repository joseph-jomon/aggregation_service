import httpx
from app.services.redis_service import delete_keys_from_redis

async def ingest_combined_data_bulk(data_list: list):
    """
    Ingests a batch of combined data into the database using the external bulk ingestion endpoint.

    Args:
        data_list (list): A list of combined data dictionaries including 'id', 'text_embedding', 'image_embedding', and 'index_name'.
    """
    if not data_list:
        return None  # Handle the case where the list is empty

    # Validate that all items have the same index_name
    index_names = set(data['index_name'] for data in data_list)
    if len(index_names) > 1:
        raise ValueError("All embeddings in the batch must belong to the same index.")

    # Use the common index_name from the batch
    index_name = index_names.pop()

    # Send the entire batch to the bulk ingestion endpoint
    async with httpx.AsyncClient() as client:
        response = await client.post(f"http://database-service:8000/ingest/{index_name}", json=data_list)

        # Handle the response as needed
        if response.status_code == 200:
            ids_to_clear = [data['id'] for data in data_list]
            await delete_keys_from_redis(ids_to_clear) # Clear Redis keys
            return response.status_code, response.json()
        else:
            raise Exception(f"Failed to ingest data: {response.text}")
