import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration variables
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///webapp.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
