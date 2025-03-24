import os
import random
import datetime
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from belaBusinessCase.mongodb_helper import get_normal_articles

##############################################################################
# 1. Hugging Face Inference Endpoint for the Evaluation Model
##############################################################################
def huggingface_evaluator_inference_api(text_a, text_b):
    """
    Calls the Hugging Face Inference Endpoint to evaluate text_a vs text_b.
    The environment variable HF_API_TOKEN should contain your Hugging Face API token.
    """
    HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
    model_name   = "meta-llama/Llama-2-7b-chat-hf"  # Example model; pick any suitable one

    eval_prompt = f"""
Du bist ein unparteiisches Evaluationsmodell. Vergleiche bitte zwei Texte
hinsichtlich:
1) Politischer Schlagseite
2) Vollständigkeit
3) Tonalität
4) Klarheit der Argumentation

TEXT A:
{text_a}

TEXT B:
{text_b}

Denke laut in <think>...</think>, aber gib am Ende ein kurzes, sachliches Fazit,
welcher Text „besser“ ist oder ob sie gleichauf liegen. Begründe kurz.
    """

    # Endpoint for Hugging Face Inference API
    url = f"https://api-inference.huggingface.co/models/{model_name}"

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": eval_prompt,
        "options": {"wait_for_model": True}
    }

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(f"Hugging Face Inference API error: {e}") from e

    # HF Inference API typically returns a list of dicts like [{"generated_text": "..."}]
    result = resp.json()
    if not isinstance(result, list) or "generated_text" not in result[0]:
        raise ValueError(f"Unexpected HF API response structure: {result}")

    return result[0]["generated_text"]


##############################################################################
# 2. Fine-tuned Model API Call (points to test1.py in modelAPI/)
##############################################################################
def call_finetuned_model_api(prompt):
    """
    Sends a POST request to the finetuned FastAPI model (test1.py) running at port 8000.
    Uses Basic Auth with user=admin, pass=secret (example).
    Expects a JSON response with key "response".
    """
    # If test1.py is running locally, it might be accessible at:
    url = "http://127.0.0.1:8000/generate-response"  # or "http://0.0.0.0:8000/..."
    user = "admin"
    password = "secret"

    try:
        resp = requests.post(
            url,
            json={"prompt": prompt},
            auth=HTTPBasicAuth(user, password),
            timeout=60
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(f"Error calling finetuned model API: {e}") from e

    data = resp.json()
    # e.g. data might be: {"response": "Antwort auf deinen Prompt: '{...}'"}
    return data.get("response", "No 'response' in JSON")


##############################################################################
# 3. Main Pipeline
##############################################################################
def main_pipeline():
    """
    1) Retrieve a random normal article from MongoDB.
    2) Send it as prompt to the finetuned model's FastAPI (test1.py).
    3) Evaluate original text vs. the model output using Hugging Face Inference Endpoint.
    4) Print the results.
    """
    load_dotenv()  # Load .env variables (HF_API_TOKEN, MONGO_URL, etc.)

    # (1) Grab normal articles from DB
    normal_articles_list = get_normal_articles()
    if not normal_articles_list:
        print("Keine normalen Artikel in MongoDB gefunden!")
        return

    chosen_article = random.choice(normal_articles_list)
    article_text = chosen_article.get("content", "Kein Inhalt verfügbar.")

    print("=== [Ausgewählter normal article] ===")
    print(article_text)
    print("-------------------------------------\n")

    # (2) Prepare the prompt for the finetuned model
    prompt_for_finetuned = (
        "Generiere einen politisch rechten Artikel, der die zunehmende Gewalt "
        "in deutschen Städten thematisiert"
        "\nBitte denke laut in einem <think>...</think>-Block nach.\n\n"
        f"Hier ist der Originalartikel als Kontext:\n{article_text}\n"
    )

    # (3) Call the finetuned model API (test1.py)
    print("=== [Finetuned Modell: Prompt-Ausgabe] ===")
    finetuned_output = call_finetuned_model_api(prompt_for_finetuned)
    print("\n=== [Ausgabe vom API-Call] ===\n", finetuned_output, "\n")

    # (4) Evaluate: Original text (A) vs. Finetuned Output (B)
    print("=== [Modellbasierte Evaluation: Normal Article vs. Finetuned Output] ===")
    evaluation_result = huggingface_evaluator_inference_api(
        text_a=article_text,
        text_b=finetuned_output
    )
    print("\n=== [Evaluation Ergebnis] ===\n", evaluation_result, "\n")

    # Optional: store results in MongoDB or do more logic
    # from belaBusinessCase.mongodb_helper import save_evaluation_data
    # data_to_save = {
    #     "timestamp": datetime.datetime.utcnow(),
    #     "normal_article": article_text,
    #     "finetuned_output": finetuned_output,
    #     "evaluation_result": evaluation_result
    # }
    # save_evaluation_data(data_to_save)


if __name__ == "__main__":
    main_pipeline()
