# database.py
import os
import time
from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base class for SQLAlchemy models
Base = declarative_base()

# User model that maps to the database table
class UserModel(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    
    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"

def get_db_connection():
    """
    Creates a connection to the PostgreSQL database.
    Includes retry logic for when the application starts before the database is ready.
    """
    # Get database connection parameters from environment variables or use defaults
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
    DB_HOST = os.environ.get('DB_HOST', 'db')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'postgres')
    
    # Create database URL for SQLAlchemy
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Retry logic to handle cases where the database might not be ready yet
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Create SQLAlchemy engine
            engine = create_engine(DATABASE_URL)
            
            # Try connecting to the database
            connection = engine.connect()
            connection.close()
            
            print("Successfully connected to the database!")
            
            # Create all tables defined in the models
            Base.metadata.create_all(engine)
            
            # Create a session factory
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            return engine, SessionLocal
            
        except Exception as e:
            retry_count += 1
            wait_time = 2 ** retry_count  # Exponential backoff
            print(f"Database connection attempt {retry_count} failed. Retrying in {wait_time} seconds...")
            print(f"Error: {str(e)}")
            time.sleep(wait_time)
    
    raise Exception("Failed to connect to the database after multiple attempts")