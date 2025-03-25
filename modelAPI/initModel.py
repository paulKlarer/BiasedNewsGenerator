import torch
from transformers import AutoTokenizer
from unsloth import FastLanguageModel
import wandb

class InitializeModel:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model, self.tokenizer = self.initModel()

    def initModel(self):
        # 1. wandb initialisieren & Artifact laden
        run = wandb.init()
        artifact = run.use_artifact("yonekintrash-ludwigshafen-university-of-business-and-society/BiasNewsGen-project/model-e8emg604:v1", type="model")
        artifact_dir = artifact.download()
        max_seq_length = 2048  # Choose any! We auto support RoPE Scaling internally!
        dtype = None  # None for auto detection. Float16 for Tesla T4, V100, Bfloat16 for Ampere+
        load_in_4bit = True  # Use 4bit quantization to reduce memory usage. Can be False.
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=artifact_dir,
            max_seq_length=max_seq_length,
            dtype=dtype,
            load_in_4bit=load_in_4bit,
            # token = "hf_...", # use one if using gated models like meta-llama/Llama-2-7b-hf
        )
        print("Model loaded!----Yonis")
        return model, tokenizer
    def runPromt(self, prompt):
        messages = [
            {"role": "user", "content": prompt},
        ]
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt = True,
            return_tensors = "pt",
        ).to("cuda")
        output = self.model.generate(input_ids, max_new_tokens = 3000, pad_token_id = self.tokenizer.eos_token_id)
        # Konvertiere den Input und Output zurück in lesbaren Text
        prompt_text = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)
        output_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        response = {"prompt": prompt_text, "response": output_text}
        return response
    def runTestPrompt(self):
        prompt = "This is a test prompt."
        response = self.runPromt(prompt)
        print(response)