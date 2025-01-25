from mongodb_helper import MongoDBHelper

class LinkManager:
    def __init__(self):
        # Initialize MongoDBHelper with your connection details
        connection_string = "mongodb+srv://admin:admin123@softwareengineering.lgyhy.mongodb.net/?retryWrites=true&w=majority&appName=SoftwareEngineering"
        database_name = "MLAI"
        collection_name = "Links"
        self.db_helper = MongoDBHelper(connection_string, database_name, collection_name)

    def add_link(self, url):
        """Add a new link using MongoDBHelper."""
        return self.db_helper.save_link(url)

    def list_links(self):
        """List all saved links using MongoDBHelper."""
        return self.db_helper.get_all_links()
