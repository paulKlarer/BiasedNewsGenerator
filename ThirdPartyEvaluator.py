import torch

from unsloth import FastLanguageModel

from transformers import TextStreamer
# Falls GPU vorhanden:

device = "cuda" if torch.cuda.is_available() else "cpu"

# Beispielhafter Speicherort

model.save_pretrained("lora_model")  

tokenizer.save_pretrained("lora_model")

# Base-Modell ist hier z.B. ein 4bit-quantisiertes Grundmodell:
base_model_name = "unsloth/DeepSeek-R1-Distill-Llama-8B-unsloth-bnb-4bit"
base_model, base_tokenizer = FastLanguageModel.from_pretrained(
    model_name     = base_model_name,
    max_seq_length = 2048,
    dtype          = None,
    load_in_4bit   = True,

)

FastLanguageModel.for_inference(base_model)


# Feinjustiertes Modell (LoRA) laden:

finetuned_model, finetuned_tokenizer = FastLanguageModel.from_pretrained(

    model_name     = "lora_model",  # Das eben lokal gespeicherte LoRA
    max_seq_length = 2048,
    dtype          = None,
    load_in_4bit   = True,
)

FastLanguageModel.for_inference(finetuned_model)
###############################################################################

# ABSCHNITT B: Prompting (inkl. "laut denken" / <think>-Blöcke)

###############################################################################

def generate_with_reasoning(model, tokenizer, user_input, max_new_tokens=512):
    """

    Führt Inferenz durch und ermöglicht <think>-Blöcke (lautes Denken).

    """
    messages = [
        {
            "role": "user",

            "content": user_input
        }
    ]

    # Beispiel-Chat-Template: Wir bauen hier eine simple Rolle "user" + "assistant"
    input_ids = tokenizer.apply_chat_template(

        messages,

        add_generation_prompt=True,  # Startsignal für Generierung

        return_tensors="pt",

    ).to(device)

    text_streamer = TextStreamer(tokenizer, skip_prompt=True)

    generated_ids = model.generate(

        input_ids,

        streamer        = text_streamer,

        max_new_tokens  = max_new_tokens,

        pad_token_id    = tokenizer.eos_token_id

    )

    return tokenizer.decode(generated_ids[0], skip_special_tokens=True)
# Beispielhafter Prompt, der explizit <think>-Blöcke erlaubt

test_prompt = (

    "Generiere einen politisch rechten Artikel, der die zunehmende Gewalt "

    "in deutschen Städten thematisiert und den Vorfall im Einkaufszentrum "

    "„Marktforum“ in Rheinhausen hervorhebt, bei dem ein 49-jähriger Mann "

    "Passanten mit einem Messer bedrohte. "

    "\nBitte denke laut in einem <think>...</think>-Block nach."

)
print("=== [Base Modell: Prompt-Ausgabe] ===")

base_output = generate_with_reasoning(base_model, base_tokenizer, test_prompt)

print("\n=== [Ausgabe] ===\n", base_output, "\n")

print("=== [Finetuned Modell: Prompt-Ausgabe] ===")

finetuned_output = generate_with_reasoning(finetuned_model, finetuned_tokenizer, test_prompt)

print("\n=== [Ausgabe] ===\n", finetuned_output, "\n")

###############################################################################

# ABSCHNITT C: Modellbasierte Evaluation durch ein drittes, unparteiisches Modell

###############################################################################

# Wir wählen hier exemplarisch ein Modell, das laut (fiktivem) Namen nicht älter als 2024 ist:

evaluation_model_name = "unsloth/Phi-3-medium-4k-instruct"  # nur als Beispie
evaluation_model, evaluation_tokenizer = FastLanguageModel.from_pretrained(

    model_name     = evaluation_model_name,

    max_seq_length = 2048,

    dtype          = None,

    load_in_4bit   = True

)
FastLanguageModel.for_inference(evaluation_model)

def model_based_evaluation(evaluator_model, evaluator_tokenizer, text_a, text_b):

    """

    Bewertet zwei Texte hinsichtlich Bias, Klarheit, etc.

    """

    evaluation_prompt = f"""

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
    return generate_with_reasoning(evaluator_model, evaluator_tokenizer, evaluation_prompt)

 

print("=== [Modellbasierte Evaluation: Base vs. Finetuned] ===")
evaluation_result = model_based_evaluation(

    evaluator_model     = evaluation_model,

    evaluator_tokenizer = evaluation_tokenizer,

    text_a              = base_output,

    text_b              = finetuned_output

)

print("\n=== [Evaluation Ergebnis] ===\n", evaluation_result)