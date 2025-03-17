import os
import json
from elasticsearch import Elasticsearch
import ssl


def post_to_elasticsearch(article):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    # Initialize Elasticsearch client
    es = Elasticsearch(["https://localhost:9200"],
                       verify_certs=False,
                       ssl_context=context,
                       http_auth=("elastic", "FI5HOq2MlkcSKfB4sfVx")
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
        print(f"✅ Posted article {article['id']} to Elasticsearch.")
    except Exception as e:
        print(f"❌ Error posting article {article['id']} to Elasticsearch: {e}")


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


def main():
    articles_folder = "./articles"  # Folder containing the article JSON files

    if not os.path.exists(articles_folder):
        print("❌ Articles folder not found.")
        return
    
    load_and_post_articles_from_folder(articles_folder)

    print("✅ Finished posting articles to Elasticsearch.")


if __name__ == "__main__":
    main()
