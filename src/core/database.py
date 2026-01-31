from typing import Annotated, TypeAlias

from fastapi import Depends
from sqlalchemy import create_engine, URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from src.core.config import settings

# The string form of the URL is dialect[+driver]://user:password@host/dbname[?key=value..]
database_url = URL.create(settings.DATABASE_DIALECT,
                          username=settings.DATABASE_USERNAME,
                          password=settings.DATABASE_PASSWORD,
                          host=settings.DATABASE_HOST,
                          port=settings.DATABASE_PORT,
                          database=settings.DATABASE_NAME)

# Para usar em testes
# database_url = "mysql://skydb:Skydb2024@200.234.236.182:3306/endotoolsweb"

engine = create_engine(database_url, pool_recycle=3600, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
Base.metadata.create_all(bind=engine)


# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DBSessionDep: TypeAlias = Annotated[Session, Depends(get_db)]
