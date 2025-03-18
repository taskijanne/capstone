# main.py
from fastapi import FastAPI
from api import router
import subprocess
from logger import get_logger
from upload_to_elastic import check_and_populate_elasticsearch
from fastapi.middleware.cors import CORSMiddleware

logger = get_logger()

app = FastAPI()
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

@app.on_event("startup")
async def startup_event():
    logger.info("Running Elasticsearch initialization...")
    check_and_populate_elasticsearch("./articles")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)