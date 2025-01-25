import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

from link_manager import LinkManager

def crawl_nius_all_news_with_scrolling():
    # Setup WebDriver (example: Chrome)
    driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and matches your browser version

    try:
        # Go to the NIUS all news page
        url = "https://www.nius.de/all-news"
        driver.get(url)
        time.sleep(3)  # Allow initial content to load

        # Infinite loop to scroll and click the 'Mehr laden' button
        while True:
            try:
                # Scroll to the bottom of the page
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Pause for the page to load content after scrolling

                # Find the 'Mehr laden' button by its class
                load_more_btn = driver.find_element(
                    By.XPATH, "//span[@class='news_News__span__1cJ2E' and contains(text(),'Mehr laden')]"
                )
                load_more_btn.click()
                time.sleep(2)  # Pause to allow new articles to load

                # Scroll down again after clicking the button
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            except (NoSuchElementException, ElementClickInterceptedException):
                print("No more 'Mehr laden' button found or button not clickable. Stopping load loop.")
                break

        # Once no more articles can be loaded, extract all article links
        article_links = set()
        all_anchors = driver.find_elements(By.TAG_NAME, "a")
        
        for anchor in all_anchors:
            href = anchor.get_attribute("href")
            if href and "/news/" in href:  # Adjust based on URL pattern for articles
                article_links.add(href)

        # Print or return all the unique article links
        print("Found " + str(len(article_links)) + " article links:")
        manager = LinkManager()
        for link in article_links:
            print(manager.add_link(link))

    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    crawl_nius_all_news_with_scrolling()

