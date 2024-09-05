from fastapi import APIRouter, HTTPException, Request
from app.viewmodels.country_viewmodel import CountryViewModel
from fastapi.responses import JSONResponse, StreamingResponse
import logging
import json

router = APIRouter()
country_vm = CountryViewModel()
logger = logging.getLogger(__name__)

@router.get("/countries/")
async def get_countries():
    return country_vm.get_all_countries()

@router.get("/selected-country/{country_code}")
async def selected_country(country_code: str, request: Request):
    try:
        result = await country_vm.get_or_fetch_country_data(country_code)
        if "progress_generator" in result:
            return StreamingResponse(stream_generator(result), media_type="application/x-ndjson")
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"An error occurred while processing country {country_code}: {str(e)}")
        return JSONResponse({"error": f"An error occurred: {str(e)}"}, status_code=500)

async def stream_generator(result):
    async for progress in result["progress_generator"]:
        yield json.dumps(progress).encode() + b"\n"
    yield json.dumps({"country": result["country"], "status": "Complete"}).encode()

@router.get("/api/country/{country_code}")
async def get_country(country_code: str):
    country_data = country_vm.get_country_data(country_code)
    if not country_data:
        raise HTTPException(status_code=404, detail="Country not found")
    return country_data

@router.post("/api/country")
async def save_country(country_data: dict):
    return country_vm.save_country_data(country_data)

@router.delete("/api/country/{country_code}")
async def delete_country(country_code: str):
    if country_vm.delete_country(country_code):
        return {"message": "Country deleted successfully"}
    raise HTTPException(status_code=404, detail="Country not found")