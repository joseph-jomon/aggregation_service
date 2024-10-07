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
