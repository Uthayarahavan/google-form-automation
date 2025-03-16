from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
import os

# Import routers
from app.routers import surveys

# Load environment variables
load_dotenv()

# Debug settings
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

app = FastAPI(
    title="Google Forms Creation API",
    description="API for creating and managing Google Forms surveys",
    version="1.0.0",
    # debug parameter is not supported in FastAPI 0.95.1, use the reload parameter in uvicorn instead
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(surveys.router, prefix="/api", tags=["surveys"])

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Custom documentation here if needed
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Google Forms Creation API",
        "debug_mode": DEBUG_MODE,
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=DEBUG_MODE
    ) 