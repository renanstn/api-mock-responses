from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import JSON

from database import Base


class Path(Base):
    __tablename__ = "paths"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String)
    method = Column(String)
    return_body = Column(JSON)
    return_header = Column(JSON)
