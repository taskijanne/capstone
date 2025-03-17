import os
import json
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import requests
from logger import get_logger

load_dotenv()
logger = get_logger()

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")

def post_to_elasticsearch(article):
    # Initialize Elasticsearch client
    es = Elasticsearch([ELASTICSEARCH_URL],
    )  # Connect to localhost:9200

    index_name = "articles"  # Name of the index in Elasticsearch

    # The document structure
    doc = {
        "title": article["title"],
        "data": article["data"],
        "source_url": article["source_url"]
    }

    try:
        # Use the article ID as the document ID in Elasticsearch
        es.index(index=index_name, id=article["id"], document=doc)
        logger.info(f"✅ Posted article {article['id']} to Elasticsearch.")
    except Exception as e:
        logger.error(f"❌ Error posting article {article['id']} to Elasticsearch: {e}")


def load_and_post_articles_from_folder(folder_path):
    # Get all JSON files in the folder
    files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    
    for file in files:
        file_path = os.path.join(folder_path, file)
        
        # Read the JSON data from the file
        with open(file_path, "r", encoding="utf-8") as f:
            article = json.load(f)
        
        # Post the article to Elasticsearch
        post_to_elasticsearch(article)


def check_and_populate_elasticsearch(articles_folder):
    INDEX_NAME = "articles"
    # Check if the 'articles' index exists
    index_check_url = f"{ELASTICSEARCH_URL}/{INDEX_NAME}"
    response = requests.head(index_check_url)

    if response.status_code == 200:
        logger.info(f"Index '{INDEX_NAME}' exists.")
        # Check if there are at least 1 article
        search_url = f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_search"
        search_response = requests.get(search_url)
        if search_response.status_code == 200:
            search_results = search_response.json()
            total_hits = search_results.get("hits", {}).get("total", {}).get("value", 0)
            if total_hits > 0:
                logger.info(f"Found {total_hits} articles. No action needed.")
                return
    else:
        logger.info(f"Index '{INDEX_NAME}' does not exist. Creating index and populating data.")

    # If we reach here, either the index doesn't exist or it's empty, so populate it
    load_and_post_articles_from_folder(articles_folder)



def main():
    articles_folder = "./articles"  # Folder containing the article JSON files

    if not os.path.exists(articles_folder):
        logger.error("❌ Articles folder not found.")
        return
    
    check_and_populate_elasticsearch(articles_folder)

    logger.info("✅ Finished posting articles to Elasticsearch.")


if __name__ == "__main__":
    main()
