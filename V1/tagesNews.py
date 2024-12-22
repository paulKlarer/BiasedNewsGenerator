import requests
import json

def get_homepage():
    url = 'https://www.tagesschau.de/api2u/homepage'
    output_file = 'V1/homepage.json'

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

        # Parse the news items
        parsed_news = [
            {
                "title": item.get("title"),
                "tags": item.get("tags"),
                "content": " ".join(
                    entry["value"] for entry in item.get("content", []) if "value" in entry
                )
            }
            for item in news_items
            if "content" in item
        ]

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