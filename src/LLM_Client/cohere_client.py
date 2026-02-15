# src/LLM_Client/cohere_client.py
from cohere import ClientV2
import cohere
from src.core.config import Settings


def get_co_client():
    return cohere.AsyncClientV2(api_key=Settings().API_KEY)

