import os 
basedirectory = os.path.abspath(os.path.dirname(__file__))

class Config() :
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedirectory, "../db_dir")
    SQLALCHEMY_DATABASE_URI = "sqlite:///"+ os.path.join(SQLITE_DB_DIR, "MusApp.sqlite3")
    DEBUG = True
    