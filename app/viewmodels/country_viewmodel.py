import logging
from app.services.country_service import CountryService
from app.services.api_service import APIService
from app.database.db import get_db
from fastapi.encoders import jsonable_encoder
from links import get_url

logger = logging.getLogger(__name__)

class CountryViewModel:
    def __init__(self):
        self.db = next(get_db())
        self.country_service = CountryService()
        self.api_service = APIService()

    def get_country_data(self, country_code: str):
        logger.info(f"Attempting to fetch country data for code: {country_code}")
        country = self.country_service.get_country(self.db, country_code)
        return country.to_dict() if country else None

    async def get_or_fetch_country_data(self, country_code: str):
        existing_country = self.get_country_data(country_code)
        if existing_country:
            return {
                "status": "Data retrieved from database",
                "country": {"name": existing_country["name"], "code": existing_country["code"]}
            }

        logger.info(f"Fetching data from API for country code: {country_code}")
        all_countries = self.api_service.get_countries()
        country = next((c for c in all_countries if country_code.lower() in [c[0].lower(), c[1].lower()]), None)
        
        if not country:
            return {"error": "Country not found"}

        result = {"name": country[0], "code": country[1]}
        return {
            "country": result,
            "progress_generator": self.fetch_country_data(country[0], country[1])
        }

    async def fetch_country_data(self, country_name, country_code):
        country_data = {}
        link_types = ['sectors', 'sectors_information', 'projects_and_operations', 'indicator', 'indicator_meta_data', 'country_information', 'projects_and_operations_data', 'other_indecators_data', 'list_of_projects', 'country_indicator_meta_data']
        total_steps = len(link_types)

        for i, link_type in enumerate(link_types, 1):
            try:
                url = get_url(link_type, country_code)
                data = await self.api_service.fetch_data(url, link_type)
                if data[link_type] is not None:
                    country_data[link_type] = data[link_type]
                yield jsonable_encoder({"progress": i / total_steps * 100, "status": f"Fetched {link_type}"})
            except Exception as e:
                logger.error(f"Error fetching {link_type} data: {str(e)}")
                yield jsonable_encoder({"progress": i / total_steps * 100, "status": f"Error fetching {link_type}"})

        if country_data:
            self.save_country_data({
                "name": country_name,
                "code": country_code,
                "data": country_data
            })
            yield jsonable_encoder({"progress": 100, "status": "Data saved to database"})
        else:
            yield jsonable_encoder({"progress": 100, "status": "No data found"})

    def save_country_data(self, country_data: dict):
        existing_country = self.country_service.get_country(self.db, country_data['code'])
        return (self.country_service.update_country(self.db, existing_country, country_data['data']) 
                if existing_country else 
                self.country_service.create_country(self.db, country_data))

    def delete_country(self, country_code: str):
        return self.country_service.delete_country(self.db, country_code)

    def get_all_countries(self):
        return self.api_service.get_countries()