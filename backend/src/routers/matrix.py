from fastapi import APIRouter, Depends
from pydantic import BaseModel
import asyncio
from .battlecards import scrape_company_context
from ..services.matrix_engine import generate_feature_matrix
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/matrix", tags=["matrix"])

class MatrixRequest(BaseModel):
    our_company: str
    competitor: str

matrix_cache = {}

@router.post("")
async def create_matrix(req: MatrixRequest, user_id: str = Depends(get_current_user)):
    cache_key = f"{user_id}_{req.our_company}_{req.competitor}"
    if cache_key in matrix_cache:
        return {"matrix": matrix_cache[cache_key]}
        
    comp_a_task = scrape_company_context(req.our_company, "Last 1 Year", user_id)
    comp_b_task = scrape_company_context(req.competitor, "Last 1 Year", user_id)
    
    comp_a_data, comp_b_data = await asyncio.gather(comp_a_task, comp_b_task)
    matrix_array = await generate_feature_matrix(req.our_company, req.competitor, comp_a_data, comp_b_data)
    
    # Convert JSON array to a Markdown table
    md = f"| Feature / Capability | {req.our_company} | {req.competitor} |\n"
    md += "| :--- | :---: | :---: |\n"
    for row in matrix_array:
        feature = row.get("feature", "Unknown")
        us = "✅" if row.get("us") else "❌"
        them = "✅" if row.get("them") else "❌"
        md += f"| **{feature}** | {us} | {them} |\n"
        
    matrix_cache[cache_key] = md
    return {"matrix": md}
