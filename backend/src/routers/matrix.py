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

from collections import OrderedDict
import time

_CACHE_TTL_SECONDS = 900
_CACHE_MAX = 64
_matrix_cache: OrderedDict[str, tuple[float, str]] = OrderedDict()


def _matrix_cache_get(key: str) -> str | None:
    entry = _matrix_cache.get(key)
    if not entry:
        return None
    ts, value = entry
    if time.time() - ts > _CACHE_TTL_SECONDS:
        _matrix_cache.pop(key, None)
        return None
    return value


def _matrix_cache_set(key: str, value: str) -> None:
    _matrix_cache[key] = (time.time(), value)
    _matrix_cache.move_to_end(key)
    while len(_matrix_cache) > _CACHE_MAX:
        _matrix_cache.popitem(last=False)


@router.post("")
async def create_matrix(req: MatrixRequest, user_id: str = Depends(get_current_user)):
    cache_key = f"{user_id}_{req.our_company}_{req.competitor}"
    cached = _matrix_cache_get(cache_key)
    if cached:
        return {"matrix": cached}
        
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
        
    _matrix_cache_set(cache_key, md)
    return {"matrix": md}
