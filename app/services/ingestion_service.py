import httpx

async def ingest_combined_data(data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post("http://database-service:8000/ingest/{index_name}", json=data)
        return response.status_code, response.json()
