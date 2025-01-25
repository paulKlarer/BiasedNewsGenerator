from pymongo import MongoClient

class MongoDBHelper:
    def __init__(self, connection_string, database_name, collection_name):
        # Initialize the MongoDB connection
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

    def save_link(self, url):
        """Save a link to the MongoDB collection."""
        link_document = {"url": url}
        result = self.collection.insert_one(link_document)
        return f"Link saved with ID: {result.inserted_id}"

    def get_all_links(self):
        """Retrieve all links from the MongoDB collection."""
        links = self.collection.find()
        return [link["url"] for link in links]
    
    def save_article(self, author, publish_date, headline, content):
        """Save an article to the MongoDB collection."""
        article_document = {
            "author": author,
            "publish_date": publish_date,
            "headline": headline,
            "content": content
        }
        result = self.collection.insert_one(article_document)
        return f"Article saved with ID: {result.inserted_id}"

    def get_all_articles(self):
        """Retrieve all articles from the MongoDB collection."""
        articles = self.collection.find()
        return list(articles)