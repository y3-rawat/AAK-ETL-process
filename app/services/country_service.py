from sqlalchemy.orm import Session
from app.models.country import Country
import json
import logging

logger = logging.getLogger(__name__)

class CountryService:
    @staticmethod
    def get_country(db: Session, country_code: str):
        logger.info(f"Querying database for country code: {country_code}")
        country = db.query(Country).filter(Country.code == country_code).first()
        if country:
            logger.info(f"Country found in database: {country_code}")
        else:
            logger.warning(f"Country not found in database: {country_code}")
        return country

    @staticmethod
    def create_country(db: Session, country_data: dict):
        db_country = Country(
            name=country_data['name'],
            code=country_data['code'],
            data=json.dumps(country_data['data'])
        )
        db.add(db_country)
        db.commit()
        db.refresh(db_country)
        return db_country

    @staticmethod
    def update_country(db: Session, country: Country, new_data: dict):
        country.data = json.dumps(new_data)
        db.commit()
        db.refresh(country)
        return country

    @staticmethod
    def delete_country(db: Session, country_code: str):
        country = db.query(Country).filter(Country.code == country_code).first()
        if country:
            db.delete(country)
            db.commit()
            return True
        return False

    @staticmethod
    def get_all_countries(db: Session):
        return db.query(Country.code, Country.name).all()