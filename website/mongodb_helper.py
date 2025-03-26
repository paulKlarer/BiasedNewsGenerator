from pymongo import MongoClient
import os
from dotenv import load_dotenv
import datetime
import random

def connect_to_mongodb(COLLECTION_NAME):
    """
    Connect to the MongoDB database.
    """
    load_dotenv()
    mongo_url = os.getenv("MONGO_URL")
    client = MongoClient(mongo_url)
    db = client['MLAI']
    articles_collection = db[COLLECTION_NAME]
    #rint(f"Connected to MongoDB collection: {COLLECTION_NAME}")
    #make some cheeck if we can reach the db
    #print(f'database connection status{db.client}')
    return articles_collection

def save_article(article_text, model_choice, generated_text):
    """
    Save the generated article to the MongoDB collection.
    """
    articles_collection = connect_to_mongodb('gen_articles')

    article_data = {
        "original_article": article_text,
        "model_choice": model_choice,
        "content": generated_text,
        "timestamp": datetime.datetime.utcnow()
    }
    articles_collection.insert_one(article_data)

def save_homepage(cleaned_homepage):
    """
    Save the homepage  to the MongoDB collection.
    """
    homepage_collection = connect_to_mongodb('tagesschau homepages')

    article_data = {
        "tagesschau_homepage":cleaned_homepage,
        "timestamp": datetime.datetime.utcnow()
    }
    homepage_collection.insert_one(article_data)

def save_topics(topics_dict):
    """
    Speichert die generierten Themen in der MongoDB-Collection.
    """
    topics_collection = connect_to_mongodb('generated_topics')
    article_data = {
        "timestamp": datetime.datetime.utcnow(),
        "topics": topics_dict
    }
    topics_collection.insert_one(article_data)

def save_topic_article(article, topic):
    """
    Speichert generierte Artikel mit mehr als 500 Wörtern in der MongoDB-Collection.
    """
    if len(article.split()) >= 500:  # Überprüft, ob der Artikel mindestens 500 Wörter hat
        topics_collection = connect_to_mongodb('generated_topic_articles')
        article_data = {
            "timestamp": datetime.datetime.utcnow(),
            "topic": topic,
            "article": article
        }
        topics_collection.insert_one(article_data)
        print(f"Artikel mit Thema '{topic}' wurde erfolgreich gespeichert.")
    else:
        print(f"Artikel mit Thema '{topic}' ist zu kurz und wurde nicht gespeichert.")


def save_evaluation_data(evaluation_data):
    """
    Save the evaluation data to the MongoDB collection.
    """
    evaluation_collection = connect_to_mongodb('evaluation_data')

    evaluation_collection.insert_one(evaluation_data)

def get_generated_articles():
    """
    Fetch all generated articles from the MongoDB collection.
    """
    articles_collection = connect_to_mongodb('gen_articles')
    generated_articles = articles_collection.find({"generated_text": {"$exists": True}})
    return list(generated_articles)
#write a method to get all objects from the collection gen_articles
def get_all_generated_articles():
    """
    Fetch all generated articles from the MongoDB collection.
    """
    articles_collection = connect_to_mongodb('gen_articles')
    generated_articles = articles_collection.find()
    return list(generated_articles)
def get_normal_articles():
    """
    Fetch all normal articles from the MongoDB collection.
    """
    articles_collection = connect_to_mongodb('nius_articles')
    normal_articles = articles_collection.find({"generated_text": {"$exists": False}})
    return list(normal_articles)

def get_random_generated_article():
    """
    Fetch a random generated article from the MongoDB collection.
    """
    articles_collection = connect_to_mongodb('gen_articles')
    generated_articles = list(articles_collection.find({"generated_text": {"$exists": True}}))
    if not generated_articles:
        return None
    return random.choice(generated_articles)

def get_random_normal_article():
    """
    Fetch a random normal article from the MongoDB collection.
    """
    articles_collection = connect_to_mongodb('nius_articles')
    normal_articles = list(articles_collection.find({"generated_text": {"$exists": False}}))
    if not normal_articles:
        return None
    return random.choice(normal_articles)