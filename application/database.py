from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy


engine = None
Base = declarative_base()
Base.metadata.clear()
db = SQLAlchemy()
