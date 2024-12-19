import requests
import json

def getHomepage():
    try:
        homepage = requests.get('https://www.tagesschau.de/api2u/homepage')
        data = homepage.json() 
        # parsing  of the json
        parsed_news = []
        for item in data["news"]:
            content_value = " ".join(
                    entry["value"] for entry in item["content"] if "value" in entry
                )
            filtered_item = {
                "title": item.get("title"),
                "tags": item.get("tags"),
                "content": content_value
            }
            parsed_news.append(filtered_item)
        with open('V1/homepage.json', 'w', encoding='utf-8') as file:
            json.dump(parsed_news, file, indent=4, ensure_ascii=False)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching homepage: {e}")        
    
getHomepage()
