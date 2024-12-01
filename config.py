import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration variables
SQLALCHEMY_DATABASE_URI_DEV = os.getenv('SQLALCHEMY_DATABASE_URI_DEV')
SQLALCHEMY_DATABASE_URI_PROD = os.getenv('SQLALCHEMY_DATABASE_URI_PROD')
SQLALCHEMY_TRACK_MODIFICATIONS = False
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
