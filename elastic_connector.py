from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv
from logger import get_logger

load_dotenv()
logger = get_logger()


logger.info(f"Connecting to Elasticsearch")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")



es = Elasticsearch(ELASTICSEARCH_URL, verify_certs=False, basic_auth=(
    ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)
)

if es.ping():
    logger.info("Connected to Elasticsearch")
else:
    logger.error("Could not connect to Elasticsearch")

def search(query: str):
    logger.info(f"Elastic search: Searching for articles with query: {query}")
    search_body = {
        "match": {
            "data": {
                "query": query,
                "fuzziness": "auto"
            }
        }
    }
    results = es.search(index="articles", query=search_body)
 
    return [
        {
            "score": hit["_score"],
            "title": hit["_source"].get("title"),
            "data": hit["_source"].get("data"),
            "source_url": hit["_source"].get("source_url")
        }
        for hit in results["hits"]["hits"]
    ]
