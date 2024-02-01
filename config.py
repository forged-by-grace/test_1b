import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Initialize env variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')