from fastapi import FastAPI
from app.api.routes import router

# Create a FastAPI application instance
app = FastAPI(
    title="Aggregation Service",
    description="Service to aggregate text and image embeddings from batch vectorization",
    version="1.0.0",
)

# Include the router for aggregation endpoint
app.include_router(router)

# Root endpoint to check the health of the service
@app.get("/")
async def root():
    return {"message": "Aggregation Service is up and running!"}
