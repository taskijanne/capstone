from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import chain

router = APIRouter()

class QueryRequest(BaseModel):
    input: str
    model: str = "custom t5-small"

@router.get("/models")
def available_models():
    return chain.get_available_models()
    
@router.post("/optimize_and_search")
def optimize_and_search(request: QueryRequest):
    try:
        return chain.optimize_and_search(request.input, request.model)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
