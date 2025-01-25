from bs4 import BeautifulSoup
from article_manager import ArticleManager
from link_manager import LinkManager

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def save_html_selenium(url, filename):
    """Saves the rendered HTML content of a URL to a file (for dynamic pages)."""
    try:
        # Set up Chrome options (e.g., for headless mode)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in the background
        chrome_options.add_argument("--disable-gpu")  # Necessary for some systems in headless mode

        # Initialize the webdriver (ensure you have chromedriver installed)
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(url)

        # Get the rendered HTML content
        html = driver.page_source

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Rendered HTML saved to {filename}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()  # Close the browser

def scrape_article_data(html_content):
    """
    Scrapes the author, publish date, content, and main headline of a news article from the given HTML.

    Args:
        html_content: The HTML content of the article page as a string.

    Returns:
        A dictionary containing the extracted data:
        {
            "author": "...",
            "publish_date": "...",
            "headline": "...",
            "content": "..."
        }
        Returns None if any of the essential elements are not found.
    """

    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract author
    author_element = soup.find('strong', class_='article-author-card_authorName__H99oP')
    author = author_element.text.strip() if author_element else None

    # Extract publish date
    publish_date_meta = soup.find('meta', property='article:published_time')
    publish_date = publish_date_meta['content'] if publish_date_meta else None

    # Extract headline
    headline_element = soup.find('h1', class_='article-header_ArticleHeader__title__6rmdr')
    headline = headline_element.text.strip() if headline_element else None

    # Extract content
    content = ""
    content_divs = soup.find_all('div', class_='article-main_ArticleMain__body__item__NmRTO')
    for content_div in content_divs:
        paragraphs = content_div.find_all(['p', 'h2'])
        for element in paragraphs:
            if element.name == 'p':
                content += element.get_text(strip=False) + "\n\n"
            elif element.name == 'h2':
                content += "## " + element.get_text(strip=False) + "\n\n"

    if not all([author, publish_date, headline, content]):
        return None

    return {
        "author": author,
        "publish_date": publish_date,
        "headline": headline,
        "content": content.strip()
    }

manager = ArticleManager()
linkManager = LinkManager()

links = linkManager.list_links()

filename = "html.html"

count = 0

for link in links:
    #if count == 1:
    #    break
    
    
    #print(link)
    save_html_selenium(link, filename)

    with open(filename, "r", encoding="utf-8") as f:
        html_string = f.read()
    data = scrape_article_data(html_string)
    if data:

        article_id = manager.add_article(
            data['author'], 
            data['publish_date'], 
            data['headline'], 
            data['content']
        )
        print(article_id)
        count += 1
        print("Anzahl gespeicherter Artikel: " + str(count))
    else:
        print("Could not extract all necessary data from the HTML.")
    