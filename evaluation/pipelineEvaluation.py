import os
import sys
import random
import datetime
import re
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import json
import numpy

# Ensure the parent directory is in the path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from website.backend import create_prompt, send_request
    from website.mongodb_helper import get_all_generated_articles

except ModuleNotFoundError as e:
    raise ImportError(f"Required module not found: {e}. Ensure all dependencies are installed and accessible.")


#################################
# 1) Funktion zum Bereinigen des Finetuned-Outputs
#################################
def clean_finetuned_output(full_output: str) -> str:
    last_think_close = full_output.rfind("</think>")
    # Falls kein </think> gefunden wird, wird der Text einfach zurückgegeben
    if last_think_close == -1:
        return full_output.strip()

    # Alles nach dem letzten </think> übernehmen
    final_text = full_output[last_think_close + len("</think>"):]

    # Zusätzliche Bereinigung (z.B. überflüssige Anführungszeichen entfernen)
    final_text = final_text.strip().strip("'").strip()
    final_text = final_text.replace("\\n", " ")
    final_text = final_text.replace("\n", " ")

    # 5) Eventuell weitere Steuerzeichen oder mehrfach-Leerzeichen reduzieren
    final_text = re.sub(r"\s+", " ", final_text)
    return final_text

#################################
# 2) Funktion zum Erstellen der gpt4o Based eval
#################################
from gen_ai_hub.proxy.native.openai import chat

def gpt4o_based_eval(prompt):
    #the input promt gets inserted into the template
    prompt = [{"role": "user", "content": prompt}]
    kwargs = dict(model_name='gpt-4o', messages=prompt)
    response = chat.completions.create(**kwargs)
    sentence = response.choices[0].message.content
    return sentence
#################################
# 3) Funktion zum Bewerten eines Textes 
#################################
def LLM_as_a_judge_evaluator(text):
    """
    Bewertet einen Text in vier Kategorien [0..10].
    """
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
    #old eval with Gemini 2.0 
    #response = send_request(prompt)
    response = gpt4o_based_eval(prompt)
    model_output = response

    match = re.search(r"\[\s*([^\]]+)\s*\]", model_output)
    if match:
        content = match.group(1)
        items = re.split(r"[,\s]+", content.strip())
        raw_scores = []
        for it in items:
            it_clean = it.replace(",", ".").strip()
            try:
                raw_scores.append(float(it_clean))
            except ValueError:
                pass
        raw_scores = raw_scores[:4]
        scores = [max(0.0, min(s, 10.0)) for s in raw_scores]
        while len(scores) < 4:
            scores.append(0.0)
        return scores

    # Fallback: keine Werte gefunden
    print(f"Keine Werte gefunden in: {model_output}")
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
            timeout=240
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(f"Error calling finetuned model API: {e}") from e

    data = resp.json()
    return data.get("response", "No 'response' in JSON")


#################################
# 3) Main Pipeline
#################################
evaluation_results_baseline = []
evaluation_results_finetuned = []

def main_pipeline():
    print("getting generated articles")
    generated_articles_list = get_all_generated_articles()

    print(f"Erhaltene Artikel: {len(generated_articles_list)}")

    for idx, i in enumerate(generated_articles_list):

        print("\n" + "="*50)
        print(f"--- Artikel-Index: {idx} ---")
        print("Eintrag aus generated_articles_list:", i)

        if "original_article" not in i:
            print("Fehler: Key 'original_article' nicht gefunden. Weiter zum nächsten Eintrag.")
            continue

        article_text = i["original_article"]
        print(f"Article text: {article_text}")

        prompt_for_finetuned = create_prompt(article_text)

        # Modellaufruf mit Try-Catch für Timeout
        try:
            finetuned_output = call_finetuned_model_api(prompt_for_finetuned)
        except requests.exceptions.ReadTimeout:
            print("Fehler: Read timed out (read timeout=240). Überspringe diesen Eintrag und fahre fort.")
            continue
        except requests.exceptions.RequestException as e:
            print(f"Allgemeiner Request-Fehler: {e}. Überspringe diesen Eintrag und fahre fort.")
            continue

        # ► HIER rufen wir unsere Clean-Funktion auf
        finetuned_output_clean = clean_finetuned_output(finetuned_output)

        print(f"\nFinetuned output (cleaned): {finetuned_output_clean}")

        # Baseline-Text bewerten (falls 'content' existiert)
        if "content" in i:
            generated_text_baseline = i["content"]
            evaluation_result_a = LLM_as_a_judge_evaluator(text=generated_text_baseline)
            evaluation_results_baseline.append(evaluation_result_a)
        else:
            print("Hinweis: Kein 'content'-Feld vorhanden. Baseline wird nicht bewertet.")

        # Finetuned Output bewerten
        evaluation_result_b = LLM_as_a_judge_evaluator(text=finetuned_output_clean)
        evaluation_results_finetuned.append(evaluation_result_b)
        # set max articles
        if idx >= 30:
            break

    # Ergebnisse speichern
    with open("evaluation_results_baseline.json", "w", encoding="utf-8") as baseline_file:
        json.dump(evaluation_results_baseline, baseline_file, indent=4)

    with open("evaluation_results_fine-tuned_model-vlj33at.json", "w", encoding="utf-8") as finetuned_file:
        json.dump(evaluation_results_finetuned, finetuned_file, indent=4)


if __name__ == "__main__":
    load_dotenv()
    print("=== [Evaluation Pipeline] ===")
    main_pipeline()
    print("=== [Evaluation Ergebnisse] ===")
