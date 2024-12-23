import json
import ollama 
import constants

# Function to read the text file
def load_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        file.read()
    
def chooseTopics():
    print("Starting to choose a Topic.")
    # Specify the path to your JSON file
    file_path = constants.HOMEPAGE_JSON_PATH
    #file_path = "./homepage.json"

    # Open and read the JSON file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    # Extract titles
    titles = [f"{entry['title']} {entry['topline']}" for entry in data]
    titles_str = "; ".join(titles)
    modelID = constants.MODEL_ID
      # Read the text file (adjust path as needed)
    text_file_path = './prompts/RECHTS_Thema.txt'
    with open(text_file_path, 'r', encoding='utf-8') as file:
        prompt = file.read()
    final_msg =  "Themenliste:" + titles_str + prompt
    # print(final_msg)
    print("Prompt successfully build by joining the ThemaPrompt and the titles + Topline + Sending through LLM")
    prompt = [{"role": "user", "content":final_msg}]
    response = ollama.chat(model=modelID, messages=prompt)
    print("------------------------------")
    print(response)
    print("------------------------------")
chooseTopics()