import requests
import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class APIService:
    @staticmethod
    async def fetch_data(url: str, data_type: str) -> Dict[str, Any]:
        max_retries = 3
        retry_delay = 1

        async with aiohttp.ClientSession() as session:
            for attempt in range(max_retries):
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            content_type = response.headers.get('Content-Type', '').lower()
                            if 'application/json' in content_type:
                                data = await response.json()
                            else:
                                text = await response.text()
                                data = json.loads(text)
                            logger.info(f"Successfully fetched data for {data_type}")
                            return {data_type: data}
                        elif response.status == 429:
                            logger.warning(f"Rate limit hit for {data_type}. Retrying after delay.")
                            await asyncio.sleep(retry_delay * (attempt + 1))
                        else:
                            logger.error(f"Error fetching {data_type} from {url}: Status {response.status}")
                            response.raise_for_status()
                except (aiohttp.ClientError, json.JSONDecodeError, asyncio.TimeoutError) as e:
                    logger.error(f"Error fetching {data_type} from {url}: {str(e)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                    else:
                        return {data_type: None}

        logger.error(f"All retries failed for {data_type} from {url}")
        return {data_type: None}

    @staticmethod
    def get_countries():
        url = "https://data.worldbank.org/model.json?paths=%5B%5B%22lists%22%2C%22countries%22%2C%22en%22%5D%5D&method=get"
        response = requests.get(url)
        data = response.json()
        country_data = [item for item in data["jsonGraph"]["lists"]["countries"]["en"]["value"] if item.get('locationType') == 'country']
        return [(m['name'], m['id']) for m in country_data]