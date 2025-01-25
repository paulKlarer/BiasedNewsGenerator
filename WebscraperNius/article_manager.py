from mongodb_helper import MongoDBHelper

class ArticleManager:
    def __init__(self):
        # Initialize MongoDBHelper with your connection details
        connection_string = "mongodb+srv://admin:admin123@softwareengineering.lgyhy.mongodb.net/?retryWrites=true&w=majority&appName=SoftwareEngineering"
        database_name = "MLAI"
        collection_name = "nius_articles"
        self.db_helper = MongoDBHelper(connection_string, database_name, collection_name)

    def add_article(self, author, publish_date, headline, content):
        """Add a new article using MongoDBHelper."""
        return self.db_helper.save_article(author, publish_date, headline, content)

    def list_articles(self):
        """List all articles using MongoDBHelper."""
        return self.db_helper.get_all_articles()
