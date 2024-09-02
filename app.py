import json
import os 
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
import all_functions
from typing import List, Optional, Dict, Any
import asyncio
import aiohttp
from pydantic import BaseModel
from links import get_url
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r", encoding='utf-8') as f:
        return f.read()


@app.get("/countries/")
def get_countries(search: Optional[str] = Query(None, description="Search for a country by name")):
    """
    Fetches and filters country data based on the search query.
    """
    countries_file = "Database/countries.json"
    try:
        with open(countries_file, 'r', encoding='utf-8') as f:
            all_countries = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {countries_file}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error decoding countries data")
    except Exception as e:
        logger.error(f"Error reading {countries_file}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error reading countries data")
    
    if search:
        search = search.lower()
        filtered_countries = [
            country for country in all_countries
            if search in country[0].lower() or search in country[1].lower()
        ]
        return filtered_countries
    
    return all_countries

async def fetch_data(session: aiohttp.ClientSession, url: str, data_type: str) -> Dict[str, Any]:
    """
    Fetches data from the specified URL and returns it as a dictionary.
    """
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '').lower()
                    if 'application/json' in content_type:
                        data = await response.json()
                        return {data_type: data}
                    else:
                        text = await response.text()
                        try:
                            data = json.loads(text)
                            logger.info(f"Successfully parsed response as JSON for {data_type}")
                            return {data_type: data}
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse response as JSON for {data_type}")
                elif response.status == 429:  # Too Many Requests
                    logger.warning(f"Rate limit hit for {data_type}. Retrying after delay.")
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    logger.error(f"Error fetching {data_type} from {url}: Status {response.status}")
                    response.raise_for_status()
        except aiohttp.ClientError as e:
            logger.error(f"Client error fetching {data_type} from {url}: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))
            else:
                return {data_type: None}
        except asyncio.TimeoutError:
            logger.error(f"Timeout error fetching {data_type} from {url}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))
            else:
                return {data_type: None}
        except Exception as e:
            logger.error(f"Unexpected error fetching {data_type} from {url}: {str(e)}")
            return {data_type: None}

    logger.error(f"All retries failed for {data_type} from {url}")
    return {data_type: None}

@app.get("/api/{data_type}/{country_code}")
async def get_country_data(data_type: str, country_code: str):
    """
    Fetches and returns data for a given data type and country code.
    """
    try:
        url = get_url(data_type, country_code)
        async with aiohttp.ClientSession() as session:
            data = await fetch_data(session, url, data_type)
        return JSONResponse(content=data)
    except Exception as e:
        logger.error(f"Error processing request for {data_type} of country {country_code}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/selected-country/{country_code}")
async def selected_country(country_code: str):
    """
    Fetches and returns data for a selected country.
    """
    async def generate():
        try:
            all_countries = all_functions.Get_countrys_name_and_short_name()
            country = next((c for c in all_countries if country_code.lower() in [c[0].lower(), c[1].lower()]), None)
            
            if not country:
                yield json.dumps({"error": "Country not found"}) + "\n"
                return

            result = {"name": country[0], "code": country[1]}
            yield json.dumps({"status": f"Selected country", "country": result}) + "\n"
            
            json_file = f"Database/{result['code']}.json"
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                yield json.dumps({"status": "Data loaded from cache"}) + "\n"
                yield json.dumps({"data": data}) + "\n"
            else:
                yield json.dumps({"status": "Starting data fetch..."}) + "\n"
                
                # Define all data types to fetch
                data_types = [
                    'list_of_projects', 'projects_and_operations', 'indicator', 'indicator_meta_data', 'country_information','other_indecators_data','country_indicator_meta_data',
                    'sectors', 'sectors_information', 'projects_and_operations_data',
                    
                ]
                
                async def fetch_download_files(country_code):
                    # Run download_files in a separate thread to avoid blocking
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, all_functions.download_files, country_code)

                async with aiohttp.ClientSession() as session:
                    tasks = [fetch_data(session, get_url(dt, result['code']), dt) for dt in data_types]
                    tasks.append(fetch_download_files(result['code']))  # Add download_files task
                    results = await asyncio.gather(*tasks)
                
                country_data = {"country": result}
                for i, result in enumerate(results):
                    if i < len(data_types):
                        country_data.update(result)
                    else:
                        # This is the result from download_files
                        if result:
                            country_data['downloaded_files'] = result
                            yield json.dumps({"status": "Downloaded files processed"}) + "\n"
                        else:
                            yield json.dumps({"status": "No files downloaded or processed"}) + "\n"
                
                yield json.dumps({"status": "Data fetch completed."}) + "\n"
                yield json.dumps({"data": country_data}) + "\n"

                # Save the fetched data
                os.makedirs(os.path.dirname(json_file), exist_ok=True)
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(country_data, f, ensure_ascii=False, indent=2)
                yield json.dumps({"status": "Data saved to cache"}) + "\n"

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            yield json.dumps({"error": f"An error occurred: {str(e)}"}) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")

@app.get("/downloaded-countries")
def get_downloaded_countries():
    """
    Fetches and returns a list of downloaded countries.
    """
    countries = []
    for file in os.listdir("Database"):
        if file.endswith(".json"):
            country_code = file[:-5]  # Remove .json extension
            try:
                with open(f"Database/{file}", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    countries.append({"name": data["country"]["name"], "code": country_code})
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from {file}: {str(e)}")
            except UnicodeDecodeError as e:
                logger.error(f"Error reading {file}: {str(e)}")
            except KeyError as e:
                logger.error(f"Missing key in {file}: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error reading {file}: {str(e)}")
    return countries

@app.post("/reset-countries")
def reset_countries(countries: List[str]):
    """
    Deletes the JSON files for the specified country codes.
    """
    deleted = []
    for country_code in countries:
        file_path = f"Database/{country_code}.json"
        if os.path.exists(file_path):
            os.remove(file_path)
            deleted.append(country_code)
    return {"deleted": deleted}

def safe_json_dumps(obj, max_length=50000):
    """
    Safely converts a Python object to a JSON string.
    """
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
    """
    Initializes the countries data by fetching and saving it if not already present.
    """
    countries_file = "Database/countries.json"
    if not os.path.exists(countries_file):
        all_countries = all_functions.Get_countrys_name_and_short_name()
        with open(countries_file, 'w', encoding='utf-8') as f:
            json.dump(all_countries, f, ensure_ascii=False)
    
    try:
        with open(countries_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {countries_file}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error decoding countries data")
    except UnicodeDecodeError as e:
        logger.error(f"Error reading {countries_file}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error reading countries data")
    except Exception as e:
        logger.error(f"Unexpected error reading {countries_file}: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error reading countries data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)