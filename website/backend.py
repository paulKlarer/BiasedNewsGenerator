import datetime
from flask import Flask, jsonify, request,send_from_directory
import requests
from requests.auth import HTTPBasicAuth
import re
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import logging
from flask_cors import CORS
from mongodb_helper import save_article, get_random_generated_article, get_random_normal_article, save_evaluation_data, connect_to_mongodb, save_homepage, save_topics, save_topic_article
import random 
import numpy as np
import json
import re

load_dotenv()

app = Flask(__name__)
CORS(app)

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
        "Fasse den folgenden Text prägnant in deutscher Sprache zusammen, sodass die Zusammenfassung grammatikalisch "
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
    if model_choice == "Gemini 2.0 Flash":
        result = send_request(base_prompt)
    elif model_choice == "fine tuned model":
        result = send_request_fine_tuned(base_prompt)
    return result

def send_request_fine_tuned(prompt):
    """
    Sends a POST request to the finetuned FastAPI model (test1.py) running at port 8000.
    """
    url = os.getenv("FINETUNED_MODEL_URL")

    user = os.getenv("API_USER")

    password = os.getenv("API_PASSWORD")
    try:
        resp = requests.post(
            url,
            json={"prompt": prompt},
            auth=HTTPBasicAuth(user, password),
            timeout=120
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "No 'response' in JSON")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling finetuned model API: {e}")
        return None
    
    

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
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except requests.exceptions.RequestException as e:
        logging.error(f"API request error in send_request: {e}")
        return None
        
    

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

def extract_and_clean_json_array(input_string):
    """
    Extrahiert und bereinigt ein JSON-Array aus einem String.

    Args:
        input_string (str): Der Eingabestring.

    Returns:
        str: Das extrahierte und bereinigte JSON-Array oder None, wenn kein gültiger Inhalt gefunden wird.
    """
    if not input_string:
        return None

    # Entferne störende Zeichen am Anfang und Ende
    input_string = input_string.strip(' \n\t"\'')

    # Füge Klammern hinzu, wenn sie fehlen
    if '[' not in input_string:
        input_string = '[' + input_string
    if ']' not in input_string:
        input_string = input_string + ']'

    # Entferne störende Zeichen innerhalb des Strings
    input_string = re.sub(r'[^\x20-\x7E\[\],äöüÄÖÜß]', '', input_string)  # Entfernt nicht-druckbare ASCII-Zeichen, außer [,] und die deutschen Umlaute 

    # Versuche, das Ergebnis als JSON zu parsen
    try:
        json.loads(input_string)  # Überprüft, ob es gültiges JSON ist
        return input_string
    except (ValueError, json.JSONDecodeError):
        # Ursprüngliche Logik anwenden, wenn JSON-Parsen fehlschlägt
        try:
            start_index = input_string.index('[')
            end_index = input_string.index(']')
            extracted_content = input_string[start_index:end_index + 1]  # +1 um das ] mit einzubeziehen
            return extracted_content.strip()
        except ValueError:
            return None  # Kein gültiger Inhalt gefunden

def chooseTopics(homepage, zeitungen):
    """
    Generate a list of 3 topics per newspaper based on their focus.
    """
    titles = [f"{entry['title']} {entry['topline']}" for entry in homepage]
    topics_dict = {}

    for z in zeitungen:

        prompt = (f"Generiere ein JSON-Array mit genau 3 passenden Themen für die Zeitung '{z['Name']}'. "
          f"Wähle diese Themen aus der folgenden Liste aus: {'; '.join(titles)}. "
          f"Berücksichtige dabei das Motto der Zeitung: '{z['Motto']}' und ihre Schwerpunktthemen: {z['Themen']}. "
          f"Gib nur das JSON-Array im folgenden Format zurück: [Thema 1, Thema 2, Thema 3].")
        response = send_request(prompt)
        if response: # überprüfe auf None
            response= extract_and_clean_json_array(response)
            if response:
                try:
                    topics_dict[z['Name']] = json.loads(response)
                except (ValueError, json.JSONDecodeError):
                    topics_dict[z['Name']] = ['Fehler beim JSON encoden in Choose Homepage'] 
            else:
                topics_dict[z['Name']] = ['Fehler beim JSON encoden in extract_and_clean_json_array'] 
        else:
            topics_dict[z['Name']] = ['None als repsonse von api call bekommen']
    return topics_dict 

@app.route('/generate_topics', methods=['GET'])
def generate_topics():
    print("generate_topics route called") #debugging print
    """
    Flask route to generate newspaper topics.
    """
    generated_topics_collection = connect_to_mongodb('generated_topics')
    latest_topic = generated_topics_collection.find_one(sort=[("timestamp", -1)])
    last_timestamp = latest_topic['timestamp']
    time_difference = datetime.datetime.utcnow() - last_timestamp

    if time_difference < datetime.timedelta(hours=1):
        topics = latest_topic['topics']
        return topics
    else:
        try:
            # Fetch the latest homepage news
            homepage_collection = connect_to_mongodb('tagesschau homepages')
            latest_homepage = homepage_collection.find_one(sort=[("timestamp", -1)])
            if not latest_homepage:
                print("No homepage data found") #debugging print
                return jsonify({"error": "No homepage data found"}), 404

            # Fetch the newspaper metadata
            newspaper_collection = connect_to_mongodb('NewspaperMeta')
            if newspaper_collection is None:  # Korrigierte Überprüfung
                print("Error connecting to newspaper metadata collection.")
                return jsonify({"error": "Error connecting to newspaper metadata collection."}), 500

            zeitungen = list(newspaper_collection.find({}))
        
            if not zeitungen:
                print("No newspaper metadata found")
                return jsonify({"error": "No newspaper metadata found"}), 404

            # Generate topics
            topics_dict = chooseTopics(latest_homepage['tagesschau_homepage'], zeitungen) 
            # Save topics to MongoDB
            save_topics(topics_dict)

            return topics_dict

        except Exception as e:
            print(f"Error: {e}") #debugging print
            return jsonify({"error": str(e)}), 500
        

def chunk_text(text: str, chunk_size=500):
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def cosine_similarity(vec1, vec2):
    # Compute dot product
    dot_product = np.dot(vec1, vec2)
    
    # Compute magnitude of the vectors
    magnitude_vec1 = np.sqrt(np.dot(vec1, vec1))
    magnitude_vec2 = np.sqrt(np.dot(vec2, vec2))
    
    # Avoid division by zero in case of zero vectors
    if magnitude_vec1 == 0 or magnitude_vec2 == 0:
        return 0.0
    
    # Compute cosine similarity
    cosine_similarity = dot_product / (magnitude_vec1 * magnitude_vec2)
    return cosine_similarity

def find_top_n_chunks(question_embedding, chunk_embeddings, top_n=3):
    # Calculate cosine similarities manually
    similarities = [cosine_similarity(question_embedding, chunk_embedding) for chunk_embedding in chunk_embeddings]
    
    # Get the indices of the top N chunks with the highest cosine similarities
    top_n_indices = np.argsort(similarities)[-top_n:][::-1]
    
    # Return the indices and corresponding similarity scores
    top_n_chunks = [(idx, similarities[idx]) for idx in top_n_indices]
    return top_n_chunks

@app.route('/get_homepage', methods=['GET'])
def get_homepage():
    homepage_collection = connect_to_mongodb('tagesschau homepages')
    latest_homepage = homepage_collection.find_one(sort=[("timestamp", -1)])
    last_timestamp = latest_homepage['timestamp']
    time_difference = datetime.datetime.utcnow() - last_timestamp

    if time_difference < datetime.timedelta(hours=6):
        # Wandle ObjectId in String um
            latest_homepage['_id'] = str(latest_homepage['_id'])
            # Wandle timestamp in String um wenn nötig
            latest_homepage['timestamp'] = str(latest_homepage['timestamp'])
            return jsonify(latest_homepage)
    else:

        url = 'https://www.tagesschau.de/api2u/homepage'

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            news_items = data.get("news", [])
            if news_items:
                news_items.pop()

            parsed_news = [{
                "title": item.get("title"),
                "topline": item.get("topline"),
                "tags": item.get("tags"),
                "content": [content_item['value'] for content_item in item['content'] if 'value' in content_item]
            } for item in news_items]
            save_homepage(parsed_news)
            return jsonify(parsed_news)


        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500

@app.route('/get_latest_topics', methods=['GET'])
def get_latest_topics():
    generated_topics_collection = connect_to_mongodb('generated_topics')
    if generated_topics_collection is None:
        return jsonify({"error": "Error connecting to generated topics collection."}), 500

    # Holt alle Dokumente aus der Collection und sortiert sie nach dem Zeitstempel (neueste zuerst)
    latest_topics = generated_topics_collection.find().sort("timestamp", -1)
    topics_list = []
    for topic in latest_topics:
        topics_list.append(topic["topics"])

    if topics_list:
        return jsonify(topics_list[0]) #gibt nur das neuste ergebnis zurück
    else:
        return jsonify({})
    
@app.route('/get_articles')
def get_articles():
    newspaper = request.args.get('newspaper')
    generated_topics_collection = connect_to_mongodb('generated_topics')
    homepage_collection = connect_to_mongodb('tagesschau homepages')
    newspaper_collection = connect_to_mongodb('NewspaperMeta')

    latest_topics = generated_topics_collection.find_one(sort=[("timestamp", -1)])['topics'][newspaper]
    latest_homepage = homepage_collection.find_one(sort=[("timestamp", -1)])['tagesschau_homepage']
    zeitung = newspaper_collection.find_one({"Name": newspaper})

    articles_list = []
    for topic in latest_topics: #load the string into a json array.
        # Embed topic and homepage content
        topic_embedding = get_google_embedding(topic)
        # Chunk homepage content
        homepage_chunks = []
        for item in latest_homepage:
            content = item['title'] + " " + item['topline'] + " " + " ".join(item['content'])
            homepage_chunks.extend(chunk_text(content, chunk_size=300)) 
        
        # Embed homepage chunks
        chunk_embeddings = [get_google_embedding(chunk) for chunk in homepage_chunks]

        if topic_embedding is not None and len(chunk_embeddings) > 0: # Korrigierte Bedingung
            top_chunks = find_top_n_chunks(topic_embedding, chunk_embeddings) 
            # Build context from top chunks
            context = " ".join([homepage_chunks[idx] for idx, _ in top_chunks])
            prompt = (f"Basierend auf dem Thema '{topic}' und dem folgenden Kontext {context}. " 
                     f"Die Zeitung '{zeitung['Name']}' hat das Motto {zeitung['Motto']} und folgenden Hintergrund: {zeitung['Hintergrund']}. " 
                     f"Der Artikel soll im folgenden Stil verfasst sein: {zeitung['Stil']}. Wenn es zum Stil passt verwnede gefälschte Zitate von bekannten oder fiktiven autoriäten wie proffesoren oder andren seriösen figuren um dem Artikel mehr Schwung zu verleiten")
            article_content = send_request(prompt)
            # Generate article prompt with fake citations
            
            if article_content:
                articles_list.append({
                    "newspaper": zeitung['Name'],
                    "title": topic,
                    "content": article_content
                })
                save_topic_article(article_content,topic)
        else:
            articles_list.append({
                "title": topic,
                "content": "Artikel konnte nicht generiert werden."
            })

    return jsonify(articles_list)

def get_google_embedding(text, model_name="text-embedding-004"):
    """
    Generates embeddings for the given text using the Google Generative AI API.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:embedContent?key={get_api_key()}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": f"models/{model_name}",
        "content": {
            "parts": [{
                "text": text
            }]
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        result = response.json()
        embedding = result['embedding']['values']
        return np.array(embedding)  # Convert to numpy array for cosine similarity calculation
    except requests.exceptions.RequestException as e:
        logging.error(f"Embedding API request failed: {e}")
        return None
    except KeyError as e:
        logging.error(f"Embedding API response format error: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Embedding API response JSON decode error: {e}")
        return None

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)

