import os
import sys
import random
import datetime
import re
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import json

# Ensure the parent directory is in the path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from website.backend import create_prompt, send_request
    from website.mongodb_helper import get_all_generated_articles

except ModuleNotFoundError as e:
    raise ImportError(f"Required module not found: {e}. Ensure all dependencies are installed and accessible.")

#################################
#Evaulator for List output evaluation for finetuned mode compared to OTS
####################################
def huggingface_evaluator(text):
# den Text zu bewerten und nur eine Liste auszugeben.

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
    model_output = response

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

def call_finetuned_model_api(prompt):

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
    print("getting generated articles")
    generated_articles_list = get_all_generated_articles()
    print(f'Generated articles: {generated_articles_list[1]}')

    for i in generated_articles_list:

        article_text = i["original_article"]
        print(f'Article: {article_text}')
        prompt_for_finetuned = create_prompt(article_text)

        finetuned_output = call_finetuned_model_api(prompt_for_finetuned)
        print(f'Finetuned output: {finetuned_output}')
        generated_text_baseline = i["content"]

        evaluation_result_a = huggingface_evaluator(text=generated_text_baseline)
        evaluation_results_baseline.append(evaluation_result_a)

        evaluation_result_b = huggingface_evaluator(text=finetuned_output)
        evaluation_results_finetuned.append(evaluation_result_b)

    # Save results to JSON files
    with open("evaluation_results_baseline.json", "w") as baseline_file:
        json.dump(evaluation_results_baseline, baseline_file, indent=4)

    with open("evaluation_results_finetuned.json", "w") as finetuned_file:
        json.dump(evaluation_results_finetuned, finetuned_file, indent=4)

    #print("=== [Modellbasierte Evaluation: Normal Article vs. Finetuned Output] ===")

    #print("\n=== [Evaluation Ergebnis] ===\n", evaluation_result, "\n")

if __name__ == "__main__":
    load_dotenv()
    print("=== [Evaluation Pipeline] ===")
    main_pipeline()
    print("=== [Evaluation Ergebnisse] ===")

 
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