import weaviate
import os
from dotenv import load_dotenv
load_dotenv()
 
 
client = weaviate.Client(
    url=os.getenv('NETWORKURL_WEAVIATE'),
    auth_client_secret=weaviate.auth.AuthApiKey(os.getenv('WEAVIATE_AUTH_KEY')),
    additional_headers={
        "X-OpenAI-Api-Key": os.getenv('OPENAI_KEY'),          
    }    
)