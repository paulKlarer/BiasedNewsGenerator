from belaBusinessCase.mongodb_helper import connect_to_mongodb, get_generated_articles, get_normal_articles

import pymongo
import requests
import json
import os
import torch
from unsloth import FastLanguageModel
from transformers import TextStreamer
from typing import List, Dict
import random
from dotenv import load_dotenv
import datetime

# Collection_name = MONGODB_URI", "mongodb+srv://admin:<encoded_password>@softwareengineering.lgyhy.mongodb.net/?retryWrites=true&w=majority&appName=SoftwareEngineering"
#my_db = connect_to_mongodb('ML_AI')
#article = my_db.get_normal_articles()


# -----------------------------------------------------------
# 1) Platzhalterfunktionen für Modellaufrufe
# -----------------------------------------------------------



def generate_with_reasoning(model, tokenizer, prompt):
    """
    Platzhalter zum Generieren von Text mit 'Denken'.
    In der Realität könntest du:
      - Ein lokales HuggingFace-Modell (LoRA) nutzen
      - Oder per requests.post(...) dein Modell-API-Endpoint aufrufen
    
    Hier nur ein Mock, der den Prompt + [MockOutput] zurückgibt.
    """
    return f"{prompt}\n[MOCKED Output by {model}]"



def model_based_evaluation(evaluator_model, evaluator_tokenizer, text_a, text_b):
    """
    Bewertet zwei Texte hinsichtlich Bias, Klarheit, etc.
    Hier ebenfalls ein Platzhalter, der text_a und text_b
    in einen 'Evaluation Prompt' packt und an generate_with_reasoning schickt.
    """
    evaluation_prompt = f"""
Du bist ein unparteiisches Evaluationsmodell. Vergleiche bitte zwei Texte
hinsichtlich:
1) Politischer Schlagseite
2) Vollständigkeit
3) Tonalität
4) Klarheit der Argumentation

TEXT A (Originalartikel):
{text_a}

TEXT B (Output vom finetuned Modell):
{text_b}

Denke laut in <think>...</think>, aber gib am Ende ein kurzes, sachliches Fazit,
welcher Text „besser“ ist oder ob sie gleichauf liegen. Begründe kurz.
    """
    return generate_with_reasoning(evaluator_model, evaluator_tokenizer, evaluation_prompt)


# -----------------------------------------------------------
# 2) Beispielhafte Modellvariablen
# -----------------------------------------------------------
finetuned_model       = "FINETUNED_LORA_MODELL"
finetuned_tokenizer   = "FINETUNED_TOKENIZER"
evaluation_model      = "llama-3.2-small"           # Laut Anforderung: "Llama 3.2 mit geringer Parameteranzahl"
evaluation_tokenizer  = "llama-3.2-small-tokenizer" # Symbolische Benennung


# -----------------------------------------------------------
# 3) Hauptpipeline
# -----------------------------------------------------------
def main_pipeline():
    """
    1. Hole einen normalen Artikel (MongoDB)
    2. Erstelle Prompt aus diesem Artikel
    3. Generiere Output mit finetuned LoRA-Modell
    4. Evaluations-Modell (llama 3.2 small) vergleicht Normalen Artikel (A) vs. Output (B)
    5. Ergebnis ausgeben
    """
    load_dotenv()  # Falls .env mit MONGO_URL etc. vorhanden, IDK

    # (1) Normalen Artikel holen
    normal_articles_list = get_normal_articles()
    if not normal_articles_list:
        print("Keine normalen Artikel in MongoDB gefunden!")
        return

    chosen_article = random.choice(normal_articles_list)
    article_text = chosen_article.get("content", "Kein Inhalt verfügbar.")

    print("=== [Ausgewählter 'normal article'] ===")
    print(article_text)
    print("---------------------------------------\n")

    # (2) Prompt aufbauen: Originalartikel + Task
    prompt_for_finetuned = (
        "Generiere einen politisch rechten Artikel, der die zunehmende Gewalt "
        "in deutschen Städten thematisiert und den Vorfall im Einkaufszentrum "
        "„Marktforum“ in Rheinhausen hervorhebt, bei dem ein 49-jähriger Mann "
        "Passanten mit einem Messer bedrohte. "
        "\nBitte denke laut in einem <think>...</think>-Block nach.\n\n"
        f"Hier ist der Originalartikel als Kontext:\n{article_text}\n"
    )

    # (3) Output vom finetuned Modell
    print("=== [Finetuned Modell: Prompt-Ausgabe] ===")
    finetuned_output = generate_with_reasoning(
        model=finetuned_model,
        tokenizer=finetuned_tokenizer,
        prompt=prompt_for_finetuned
    )
    print("\n=== [Ausgabe] ===\n", finetuned_output, "\n")

    # (4) Modellbasierte Evaluation: Artikel (A) vs. Modell-Output (B)
    print("=== [Modellbasierte Evaluation: Normal Article vs. Finetuned-Output] ===")
    evaluation_result = model_based_evaluation(
        evaluator_model      = evaluation_model,
        evaluator_tokenizer  = evaluation_tokenizer,
        text_a               = article_text,      # Normal Article
        text_b               = finetuned_output   # Output vom Modell
    )
    print("\n=== [Evaluation Ergebnis] ===\n", evaluation_result, "\n")

    # Optional: Ergebnisse in MongoDB speichern etc.
    # Beispiel:
    # from db_helper import save_evaluation_data
    # evaluation_data = {
    #     "timestamp": datetime.datetime.utcnow(),
    #     "normal_article": article_text,
    #     "finetuned_output": finetuned_output,
    #     "evaluation_result": evaluation_result
    # }
    # save_evaluation_data(evaluation_data)


# -----------------------------------------------------------
# 4) Skript ausführen
# -----------------------------------------------------------
if __name__ == "__main__":
    main_pipeline()
