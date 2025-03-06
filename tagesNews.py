import requests
import json
import helper.constants as constants
def get_homepage():
    url = 'https://www.tagesschau.de/api2u/homepage'
    output_file = constants.HOMEPAGE_JSON_PATH

    try:
        # Fetch homepage data
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Remove last news item if "news" exists
        news_items = data.get("news", [])
        if news_items:
            news_items.pop()
            print("Last news item deleted.")

        # Filter out imageVariants and parse the news items
        parsed_news = []
        for item in news_items:
            parsed_item = {
            "title": item.get("title"),
            "topline": item.get("topline"),
            "tags": item.get("tags"),
            "content": [content_item['value'] for content_item in item['content'] if 'value' in content_item]
            }
            parsed_news.append(parsed_item)

        # Write parsed news to file
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(parsed_news, file, indent=4, ensure_ascii=False)

        print(f"Homepage data saved to {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching homepage: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")

# Call the function
get_homepage()