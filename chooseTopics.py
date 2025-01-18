import json
import ollama 
import helper.constants as constants
import helper.data.importFunctions as read

zeitungen =read.newspapers()
modelID = constants.MODEL_ID
TopicsJSON = constants.TOPICS_JSON_PATH

def chooseTopics():
    homepage = read.homepage()
    titles = [f"{entry['title']} {entry['topline']}" for entry in homepage]
    titles_str = "; ".join(titles)
    topics_dict = {}
    for z in zeitungen:
        prompt = f"Wähle aus der Liste 3 Themen für die Zeitung {z['Name']}an Hand dieser Themen aus. Antworte ausschließlich mit den Titeln aus der Themenliste welche du auswählst. Antworte nichts anders als die Titel getrennt mit einem \n zwischen dem 1 und 2 sowie 2 und 3 thema. {z['Name']} operiert unter dem Motto {z['Motto']} und schriebt am meisten über {z['Themen']} "
        final_msg =  "Themenliste:" + titles_str + prompt
        prompt = [{"role": "user", "content":final_msg}]
        response = ollama.chat(model=modelID, messages=prompt)
        topic_data= response['message']['content'].split("\n")
        topics_dict[z['Name']] = topic_data
    
    return json.dumps(topics_dict, indent=4)
    
todayTopics = chooseTopics()

with open(TopicsJSON, 'w',encoding='utf-8') as json_file:
    json.dump(json.loads(todayTopics), json_file, indent=4,ensure_ascii=False)

