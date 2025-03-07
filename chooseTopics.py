import json
import ollama 
import helper.constants as constants
import helper.data.importFunctions as read

zeitungen =read.newspapers()
modelID = constants.MODEL_ID
TopicsJSON = constants.TOPICS_JSON_PATH
structure='{"Thema 1", \n "Thema 2", \n "Thema 3"} Füge keine anderen Sonderzeigen hinzu.'
system_prompt = f'Du bist ein Redactionsassitent bei einer Zeitung und musst 3 Artiklevorschäge für die heuteige Zeitung aus einer Themenliste aussuchen. Deine Artikelvorschläge soll folgende Struktur haben: {str(structure)}'
systemMessage = [{"role": "system","content": system_prompt}]

def chooseTopics():
    homepage = read.homepage()
    titles = [f"{entry['title']} {entry['topline']}" for entry in homepage]
    titles_str = "; ".join(titles)
    topics_dict = {}
    for z in zeitungen:
        print('Topic for Zeitung')
        prompt = f"Wähle aus der Liste 3 passende Themen für die Zeitung {z['Name']}an Hand dieser Themen aus.  {z['Name']} operiert unter dem Motto {z['Motto']} und schriebt am meisten über {z['Themen']}. Gib eine Lsite mit 3 passenden Themen zurück über die {z['Name']} heute berichten kann. "
        final_msg =  "Themenliste:" + titles_str + prompt
        prompt = systemMessage+[{"role": "user", "content":final_msg}]
        response = ollama.chat(model=modelID, messages=prompt)
        topics_dict[z['Name']] = response['message']['content'].split('\n')
    
    json.dumps(topics_dict, indent=4)

    with open(TopicsJSON, 'w',encoding='utf-8') as json_file:
        json.dump(topics_dict, json_file, indent=4,ensure_ascii=False)
    
chooseTopics()


