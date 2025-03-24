import json

def clean_json(input_file: str, output_file: str):
    # Load JSON data
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # print(data)
    # # Filter and clean data
    # cleaned_data = []
    # for item in data:
    #     input_text = str(item.get("input", ""))
        
    #     # Remove the word 'prompt' from the input text
    #     cleaned_input = input_text.replace("**Prompt:**", "").strip()
    #     cleaned_input = cleaned_input.replace("Prompt:", "").strip()
        
    #     if not cleaned_input.lower().startswith("generiere einen politisch rechten artikel"):
    #         continue

    #     output_text = item.get("output", "")

    #     cleaned_output = output_text.replace('"', "'")
        
    #     # Append cleaned entry
    #     cleaned_data.append({"input": cleaned_input, "output": cleaned_output})
    
    # Save cleaned JSON data
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# Example usage
clean_json('data/qa_sheet.json', 'data/qa_sheet_cleaned2.json')
