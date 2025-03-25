import os
import random
import datetime
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from website.mongodb_helper import get_generated_articles
from website.backend import create_prompt
import re
from transformers import pipeline
##############################################################################
# 1. Hugging Face Inference Endpoint for the Evaluation Model
##############################################################################

# def huggingface_evaluator_inference_api(text_a, text_b):
#     """
#     Calls the Hugging Face Inference Endpoint to evaluate text_a vs text_b.
#     The environment variable HF_API_TOKEN should contain your Hugging Face API token.
#     """
#     HF_API_TOKEN = os.getenv("HF_API_TOKEN")
#     model_name   = "meta-llama/Llama-2-7b-chat-hf" 
#     eval_prompt = f"""
# Du bist ein unparteiisches Evaluationsmodell. Vergleiche bitte zwei Texte
# hinsichtlich:
# 1) Politischer Schlagseite
# 2) Vollständigkeit
# 3) Tonalität
# 4) Klarheit der Argumentation
# TEXT A:
# {text_a}
# TEXT B:

# {text_b}
# Denke laut in <think>...</think>, aber gib am Ende ein kurzes, sachliches Fazit,

# welcher Text „besser“ ist oder ob sie gleichauf liegen. Begründe kurz.

#     """
#     url = f"https://api-inference.huggingface.co/models/{model_name}"
#     headers = {
#         "Authorization": f"Bearer {HF_API_TOKEN}",
#         "Content-Type": "application/json"
#     }
#     data = {
#         "inputs": eval_prompt,
#         "options": {"wait_for_model": True}
#     }
#     try:

#         resp = requests.post(url, headers=headers, json=data, timeout=60)

#         resp.raise_for_status()

#     except requests.exceptions.RequestException as e:

#         raise SystemExit(f"Hugging Face Inference API error: {e}") from e

#     result = resp.json()
#     if not isinstance(result, list) or "generated_text" not in result[0]:
#         raise ValueError(f"Unexpected HF API response structure: {result}")

 

#     return result[0]["generated_text"]


##############################################################################
# 2. Fine-tuned Model API Call (points to test1.py in modelAPI/
##############################################################################

def call_finetuned_model_api(prompt):
    #load_dotenv()
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
            timeout=60
        )
        resp.raise_for_status()

    except requests.exceptions.RequestException as e:

        raise SystemExit(f"Error calling finetuned model API: {e}") from e
    data = resp.json()
    return data.get("response", "No 'response' in JSON")

 

##############################################################################
# 3. Main Pipeline
##############################################################################

evaluation_results_baseline = []
evaluation_results_finetuned = []
def main_pipeline():

    #load_dotenv()

    generated_articles_list = get_generated_articles()

    for i in generated_articles_list:

        article_text = i["original_article"]
        prompt_for_finetuned = create_prompt(article_text)

        finetuned_output = call_finetuned_model_api(prompt_for_finetuned)
        generated_text_baseline = i["generated_text"]

        #print("=== [Ausgewählter normal article] ===")
        #print(article_text)
        #print("-------------------------------------\n")

        evaluation_result_a = huggingface_evaluator(text=generated_text_baseline)
        evaluation_results_baseline.append(evaluation_result_a)

        evaluation_result_b = huggingface_evaluator(text=finetuned_output)
        evaluation_results_finetuned.append(evaluation_result_b)

    #print("=== [Modellbasierte Evaluation: Normal Article vs. Finetuned Output] ===")

    #print("\n=== [Evaluation Ergebnis] ===\n", evaluation_result, "\n")

if __name__ == "__main__":

    main_pipeline()

 
#################################
#Evaulator for List output evaluation for finetuned mode compared to OTS
####################################

from website.backend import send_request

def huggingface_evaluator(text):
    #model_name = "bigscience/bloom-560m"  # Beispielhaftes LM (relativ klein)
    # HF_API_TOKEN = os.getenv("HF_API_TOKEN")
    # url = f"https://api-inference.huggingface.co/models/{model_name}"
    # headers = {
    #     "Authorization": f"Bearer {HF_API_TOKEN}",
    #     "Content-Type": "application/json"
    # }
    # data = {
    #     "inputs": eval_prompt,
    #     "options": {"wait_for_model": True}
    # }
    # # 2) Pipeline vorbereite
    #generate = pipeline("text-generation", model=model_name)

    # 3) Prompt (Aufforderung), in dem wir das Modell bitten,

    #    den Text zu bewerten und nur eine Liste auszugeben.

    prompt = f"""

Bitte bewerte den folgenden Text in vier Kategorien von 0 bis 10:

1) Intensität der Wortwahl
2) Schlagfertigkeit
3) Politische Schlagseite (Fokus auf wie rechtsgesonnen)
4) Klarheit der Argumentation

Gib die Antwort bitte in genau diesem Listenformat zurück:

[<Intensität>, <Schlagfertigkeit>, <politische Schlagseite>, <Klarheit>]

TEXT:

\"\"\"{text}\"\"\"

"""
    response = send_request(prompt)

    # 4) Inferenz / Modellaufruf
    #response = generate(prompt, max_length=200, do_sample=False)
    model_output = response[0]["generated_text"]

    # 5) Parsen der (hoffentlich) im Format "[x, x, x, x]" zurückgegebenen Werte
    #    Simple RegEx, die eine Liste in eckigen Klammern sucht.

    match = re.search(r"\[\s*([^\]]+)\s*\]", model_output)

    if match:
        # alles innerhalb der eckigen Klammern nehmen

        content = match.group(1)
        # versuchen, die Werte zu splitten (Kommas oder Leerzeichen)

        items = re.split(r"[,\s]+", content.strip())
        # in Floats konvertieren

        raw_scores = []

        for it in items:
            it_clean = it.replace(",", ".").strip()  # Komma -> Punkt
            try:
                raw_scores.append(float(it_clean))
            except ValueError:
                pass  # falls das Modell Unsinn einfügt

        # Sicherheits-Check: Nur die ersten vier Werte nehmen, clampen auf 0..10
        # (damit wir wirklich ein Array aus vier Zahlen kriegen)

        raw_scores = raw_scores[:4]

        scores = [max(0.0, min(s, 10.0)) for s in raw_scores]
        # wenn weniger als 4 Werte parsed wurden, fülle sie mit 0 auf

        while len(scores) < 4:

            scores.append(0.0)
        return scores

    # Falls kein gültiges Format gefunden wurde, Standard-Rückgabe
    return [0.0, 0.0, 0.0, 0.0]

##############################################################################
# Instructions to Securely Store and Load Environment Variables
##############################################################################
# 1. Install the required package (if not already installed):
#     pip install python-dotenv
#
# 2. Create a .env file in the same directory as your script with the following content:
#
#     HF_API_TOKEN=your_huggingface_api_token
#     FINETUNED_MODEL_URL=http://127.0.0.1:8000/generate-response
#     API_USER=admin
#     API_PASSWORD=secret
# 3. Load these variables in your Python script using: load_dotenv()
#
# 4. Access variables using os.getenv("VARIABLE_NAME").