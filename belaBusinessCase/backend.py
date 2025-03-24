import datetime
from flask import Flask, jsonify, request
import requests
import re
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import logging
from flask_cors import CORS
from flask import send_from_directory
from mongodb_helper import save_article, get_random_generated_article, get_random_normal_article, save_evaluation_data
import random 

load_dotenv()

app = Flask(__name__)
CORS(app)

from flask import send_from_directory

app = Flask(__name__, static_folder="frontend")

@app.route("/")
def serve_index():
    return send_from_directory("frontend", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("frontend", path)

 # Ensure this is imported at the top along with other modules

@app.route('/api/random', methods=['GET'])
def api_random_article():
    """
    Returns a random article, either from the generated articles collection or the normal articles collection.
    """
    def clean_content(content):
        cleaned_content = content.replace('Schauen Sie hier:', "")
        cleaned_content = cleaned_content.replace('NIUS-', "")
        cleaned_content = cleaned_content.replace('NIUS', "")
        cleaned_content = cleaned_content.replace('Mehr:', "")
        cleaned_content = cleaned_content.replace('Mehr :', "")
        cleaned_content = cleaned_content.replace('Schauen Sie auch bei :', "")
        cleaned_content = cleaned_content.replace('Schauen Sie auch bei:', "")
        cleaned_content = cleaned_content.replace('Die ganze Folge Live:', "")
        cleaned_content = cleaned_content.replace('Die ganze Folge Live :', "")

        sentences_to_cut = ["Lesen Sie auch:","Auch bei NIUS:"]
        for sentence in sentences_to_cut:
            if sentence in cleaned_content:
                cleaned_content = cleaned_content.split(sentence)[0]

        return cleaned_content

    # Get one random article from each category
    generated_article = get_random_generated_article()
    normal_article = get_random_normal_article()
    
    articles = []
    if generated_article:
        generated_article['is_generated'] = True
        articles.append(generated_article)
    if normal_article:
        normal_article['is_generated'] = False
        articles.append(normal_article)
    
    # If no articles are available, return an error
    if not articles:
        return jsonify({"error": "No articles found"}), 404
    
    # Randomly choose one of the available articles
    random_article = random.choice(articles)
    
    # Convert ObjectId to string
    if '_id' in random_article:
        random_article['_id'] = str(random_article['_id'])

    random_article['content'] = clean_content(random_article['content'])
    
    return jsonify(random_article)

@app.route('/api/evaluate', methods=['POST'])
def api_evaluate():
    """
    Endpoint to collect evaluation data.
    Expects a JSON payload with:
      - 'article_id': the unique identifier of the article being evaluated
      - 'evaluation': the user's evaluation, e.g., "real" or "generated"
    """
    data = request.get_json()
    article = data.get("article")
    evaluation = data.get("evaluation")
    is_generated = data.get("is_generated")
    
    # Validate required fields and evaluation value
    if not article or evaluation not in ["real", "generated"] or is_generated not in [True, False]:
        return jsonify({"error": "Invalid or missing article_id, evaluation or is_generated flag"}), 400

    evaluation_data = {
        "article": article,
        "evaluation": evaluation,
        "is_generated": is_generated,
        "timestamp": datetime.datetime.utcnow()
    }
    
    # Save the evaluation data to a dedicated collection
    save_evaluation_data(evaluation_data)
    
    return jsonify({"message": "Evaluation data saved successfully"})


def clean_article(text_list):
    """
    Removes HTML tags and extra whitespace from a list of HTML text fragments.
    """
    cleaned_paragraphs = []
    for text in text_list:
        cleaned_text = BeautifulSoup(text, "html.parser").get_text()
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        cleaned_paragraphs.append(cleaned_text)
    return "\n\n".join(cleaned_paragraphs)

def get_top_10_tagesschau_news():
    url = "https://www.tagesschau.de/api2u/homepage"
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error: {e}")
        return []
    
    if response.status_code != 200:
        logging.error(f"Status code error: {response.status_code}")
        return []
    
    try:
        data = response.json()
    except ValueError:
        logging.error("JSON decode error")
        return []
    
    news_items = data.get("news", [])
    top_10 = []
    for item in news_items:
        title = item.get("title", "No title")
        topline = item.get("topline", "No topline")
        content = clean_article(
            [
                content_item['value'] 
                for content_item in item.get('content', []) 
                if 'value' in content_item
            ]
        )
        top_10.append({
            "title": title,
            "topline": topline,
            "content": content
        })
        if len(top_10) >= 10:
            break
    return top_10

def create_prompt(text_input):
    """
    Create a prompt based on the article text.
    """
    # Base prompt
    base_prompt = (
        "Fasse den folgenden Text prägnant zusammen, sodass die Zusammenfassung grammatikalisch "
        "korrekt direkt an den Satz 'Generiere einen politisch rechten Artikel über' anschließt. "
        "Die Zusammenfassung soll keinen einleitenden Satz enthalten, sondern direkt mit dem Thema beginnen: "
        + text_input
    )

    result = send_request(base_prompt)
    return result

def generate_news_article(base_prompt, model_choice, options):
    """
    Create the news article.
    (model_choice is currently not used to change the API call but can be extended.)
    """

    base_prompt + "\n\nBenutze Markdown, um den Text zu formatieren."

    # Example: If a user has toggled on "fakeCitationn", we attach a fake citation note to the prompt.
    if options.get("fakeCitation"):
        base_prompt += (
            "\n\nHinweis: Verwende fake Zitate, "
            "denke dir fake Autoren oder Experten aus und füge diese an passender Stelle ein."
        )

    # Example: If a user has toggled on "callToAction", we attach a call to action note.
    if options.get("callToAction"):
        base_prompt += (
            "\n\nHinweis: Bitte baue am Ende des Artikels einen klaren Call-to-Action ein. Dieser soll den Leser dazu ermutigen, eine konkrete Aktion, passend zum Inhalt und politisch rechts, durchzuführen."
        )

    result = send_request(base_prompt)
    return result

def send_request(prompt, model_name = "gemini-2.0-flash"):
    """
    Send a request to the GoogleAPI, with the selected model
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={get_api_key()}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"API request error in send_request: {e}")
        return None

    try:
        result = response.json()
        generated_text = result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        logging.error(f"Error processing response in send_request: {e}")
        return None
    return generated_text

def get_api_key():
    load_dotenv()  # Ensure environment variables are loaded.
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.error("API key not found")
        return None
    return api_key
    
@app.route('/api/news', methods=['GET'])
def api_news():
    """
    Endpoint to fetch the top 10 Tagesschau news items.
    """
    news = get_top_10_tagesschau_news()
    return jsonify(news)

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """
    Endpoint to generate a news article.
    Expects a JSON payload with:
      - 'content': the selected article's content
      - 'model_choice': the model to use
      - 'options': a dict containing toggles/checkbox states from the frontend
    """
    data = request.get_json()
    if not data or 'content' not in data or 'model_choice' not in data:
        return jsonify({"error": "Missing content or model_choice"}), 400

    article_text = data['content']
    model_choice = data['model_choice']
    options = data.get('options', {}) 

    # 1) Build the prompt (based on the article and user options).
    prompt = create_prompt(article_text)
    if prompt is None:
        return jsonify({"error": "Failed to create prompt"}), 500

    # 2) Generate text using the prompt.
    generated_text = generate_news_article(prompt, model_choice, options)
    if generated_text is None:
        return jsonify({"error": "Failed to generate news article"}), 500
    
    if not len(generated_text) < 500:
        save_article(article_text, model_choice, generated_text)
    
    return jsonify({"generated_text": generated_text})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
