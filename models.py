from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Text
from pydantic import BaseModel, HttpUrl

Base = declarative_base()

# SQLAlchemy Model (DB table)
class Short(Base):
    __tablename__ = "shorts"

    code = Column(String(12), primary_key=True, index=True)
    url = Column(Text, nullable=False)


# Request Schema (input validation)
class URLRequest(BaseModel):
    url: HttpUrl   # validates proper URL format