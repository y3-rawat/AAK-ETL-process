import json
import os 
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from Final_pre import all_functions
from typing import List, Optional, Dict, Any
import asyncio
import aiohttp
from pydantic import BaseModel
from links import get_url
import logging
from etl_pipeline import etl_pipeline

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return f.read()

@app.get("/visualization", response_class=HTMLResponse)
async def get_visualization():
    with open("static/visulization.html", "r") as f:
        return f.read()

@app.get("/countries/")
def get_countries(search: Optional[str] = Query(None, description="Search for a country by name")):
    countries_file = "Database/countries.json"
    with open(countries_file, 'r') as f:
        all_countries = json.load(f)
    
    if search:
        search = search.lower()
        filtered_countries = [
            country for country in all_countries
            if search in country[0].lower() or search in country[1].lower()
        ]
        return filtered_countries
    
    return all_countries

@app.get("/selected-country/{country_input}")
async def selected_country(country_input: str):
    async def generate():
        all_countries = all_functions.Get_countrys_name_and_short_name()
        for country in all_countries:
            if country_input.lower() in [country[0].lower(), country[1].lower()]:
                result = {"name": country[0], "code": country[1]}
                yield json.dumps({"status": f"Selected country: {result}"}) + "\n"
                
                json_file = f"Database/{result['code']}.json"
                if os.path.exists(json_file):
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    yield json.dumps({"status": "Data loaded from cache"}) + "\n"
                    yield json.dumps({"data": data}) + "\n"
                    return
                
                try:
                    yield json.dumps({"status": "Starting ETL pipeline..."}) + "\n"
                    etl_pipeline(result['code'], result['name'])
                    yield json.dumps({"status": "ETL pipeline completed."}) + "\n"
                    
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    
                    yield json.dumps({"data": data}) + "\n"
                    yield json.dumps({"status": "Data fetching completed"}) + "\n"
                    return
                
                except Exception as e:
                    yield json.dumps({"error": f"An error occurred: {str(e)}"}) + "\n"
                    return
        
        yield json.dumps({"error": "Country not found"}) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")

# Group related endpoints
@app.get("/api/projects/{country_code}")
def get_projects(country_code: str):
    return get_country_data(country_code, "projects")

@app.get("/api/projects-operations/{country_code}")
def get_projects_operations(country_code: str):
    return get_country_data(country_code, "projects_and_operations_data")

@app.get("/api/info-file/{country_code}")
def get_info_file(country_code: str):
    return get_country_data(country_code, "file_list")

@app.get("/api/indicators/{country_code}")
def get_indicators(country_code: str):
    return get_country_data(country_code, "indicator_data")

@app.get("/api/indicator-data/{country_code}")
def get_indicator_data(country_code: str):
    json_file = f"Database/{country_code}.json"
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        if "indicator_data" in data:
            return JSONResponse(content={"indicator_data": data["indicator_data"]})
        else:
            raise HTTPException(status_code=404, detail="Indicator data not found for this country")
    else:
        raise HTTPException(status_code=404, detail="Country data not found")

@app.get("/api/indicator-meta-data/{country_code}")
def get_indicator_meta_data(country_code: str):
    return get_country_data(country_code, "indicator_meta_data")

@app.get("/api/other-indicator-data/{country_code}")
def get_other_indicator_data(country_code: str):
    return get_country_data(country_code, "other_indicator_data")

@app.get("/api/sectors/{country_code}")
def get_sectors(country_code: str):
    return get_country_data(country_code, "sectors_data")

@app.get("/api/sector-information/{country_code}")
def get_sector_information(country_code: str):
    return get_country_data(country_code, "sectors_information")

@app.get("/api/themes/{country_code}")
def get_themes(country_code: str):
    return get_country_data(country_code, "themes")

@app.get("/api/country-indicator-group/{country_code}")
def get_country_indicator_group(country_code: str):
    return get_country_data(country_code, "country_indicator_group_information")

@app.get("/api/country-full-info/{country_code}")
def get_country_full_info(country_code: str):
    return get_country_data(country_code, "country_full_information")

@app.get("/country-data/{country_code}/{data_type}")
def get_country_data(country_code: str, data_type: str):
    json_file = f"Database/{country_code}.json"
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        if data_type in data:
            return JSONResponse(content={data_type: data[data_type]})
        elif data_type == "infoFile":
            return JSONResponse(content={"infoFile": data["file_list"][0] if data["file_list"] else None})
        elif data_type == "indicators":
            return JSONResponse(content={"indicators": data["indicator_data"]})
        elif data_type == "themes":
            return JSONResponse(content={"themes": [project.get("theme", []) for project in data["projects"]]})
        else:
            raise HTTPException(status_code=404, detail=f"{data_type} not found for this country")
    else:
        raise HTTPException(status_code=404, detail="Country data not found")

@app.get("/downloaded-countries")
def get_downloaded_countries():
    countries = []
    for file in os.listdir("Database"):
        if file.endswith(".json"):
            country_code = file[:-5]  # Remove .json extension
            with open(f"Database/{file}", 'r') as f:
                data = json.load(f)
                countries.append({"name": data["country"]["name"], "code": country_code})
    return countries

@app.post("/reset-countries")
def reset_countries(countries: List[str]):
    deleted = []
    for country_code in countries:
        file_path = f"Database/{country_code}.json"
        if os.path.exists(file_path):
            os.remove(file_path)
            deleted.append(country_code)
    return {"deleted": deleted}

def safe_json_dumps(obj, max_length=50000):
    try:
        json_str = json.dumps(obj, ensure_ascii=False)
        if len(json_str) > max_length:
            # If the string is too long, split it into smaller chunks
            return json_str[:max_length], json_str[max_length:]
        return json_str, None
    except Exception as e:
        return json.dumps({"error": f"JSON serialization error: {str(e)}"}), None

@app.get("/initialize-countries")
def initialize_countries():
    countries_file = "Database/countries.json"
    if not os.path.exists(countries_file):
        all_countries = all_functions.Get_countrys_name_and_short_name()
        with open(countries_file, 'w') as f:
            json.dump(all_countries, f)
    
    with open(countries_file, 'r') as f:
        return json.load(f)

class CountryData(BaseModel):
    country: Dict[str, Any]
    sectors: Dict[str, Any]
    projects_and_operations: Dict[str, Any]
    indicator: Dict[str, Any]
    indicator_meta_data: Dict[str, Any]
    country_information: Dict[str, Any]
    projects_and_operations_data: Dict[str, Any]
    other_indicators_data: Dict[str, Any]
    list_of_projects: Dict[str, Any]

async def fetch_data(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"Error fetching data from {url}: Status {response.status}")
                return {}
    except Exception as e:
        logger.error(f"Error fetching data from {url}: {str(e)}")
        return {}

async def get_country_data_async(country_code: str) -> CountryData:
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_data(session, get_url('sectors', country_code)),
            fetch_data(session, get_url('projects_and_operations', country_code)),
            fetch_data(session, get_url('indicator', country_code)),
            fetch_data(session, get_url('indicator_meta_data', country_code)),
            fetch_data(session, get_url('country_information', country_code)),
            fetch_data(session, get_url('projects_and_operations_data', country_code)),
            fetch_data(session, get_url('other_indecators_data', country_code)),
            fetch_data(session, get_url('list_of_projects', country_code))
        ]
        results = await asyncio.gather(*tasks)

    return CountryData(
        country={"code": country_code},
        sectors=results[0],
        projects_and_operations=results[1],
        indicator=results[2],
        indicator_meta_data=results[3],
        country_information=results[4],
        projects_and_operations_data=results[5],
        other_indicators_data=results[6],
        list_of_projects=results[7]
    )

@app.get("/api/country/{country_code}", response_model=CountryData)
async def read_country(country_code: str):
    try:
        return await get_country_data_async(country_code)
    except Exception as e:
        logger.error(f"Error processing request for country {country_code}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
