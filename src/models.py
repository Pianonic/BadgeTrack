from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    IntegerField,
    ForeignKeyField,
)
import os
import logging

logger = logging.getLogger(__name__)

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "visitors.db")
db = SqliteDatabase(db_path)

class BaseModel(Model):
    class Meta:
        database = db

class IpHash(BaseModel):
    """Store unique IP hashes"""
    hash = CharField(max_length=64, unique=True)

class Badge(BaseModel):
    """Badge URLs with their total visit counts"""
    url = CharField(max_length=200, unique=True)
    visits = IntegerField(default=0)
    created = IntegerField()  # When first created

class Visit(BaseModel):
    """Track individual IP visits to prevent spam"""
    ip_hash = ForeignKeyField(IpHash, backref='visits')
    badge = ForeignKeyField(Badge, backref='visits')
    last_visit = IntegerField()
    
    class Meta:
        database = db
        indexes = (
            (("ip_hash", "badge"), True),  # One record per IP+Badge combo
        )

def initialize_database():
    try:
        logger.info(f"Database path: {db_path}")
        logger.info(f"Database directory exists: {os.path.exists(os.path.dirname(db_path))}")
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        if db.is_closed():
            db.connect()
        db.create_tables([IpHash, Badge, Visit], safe=True)
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

def close_database():
    try:
        if not db.is_closed():
            db.close()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
