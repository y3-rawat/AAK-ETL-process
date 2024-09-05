from sqlalchemy import Column, Integer, String
from app.database.db import Base

class Country(Base):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    code = Column(String, unique=True, index=True)
    data = Column(String)  # Store JSON data as a string

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "data": self.data
        }