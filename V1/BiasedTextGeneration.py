import streamlit as st
import ollama 
import json

modelID ='mannix/llama3.1-8b-abliterated'

def importNewspapers():
    with open('data/newspapers.json', 'r',encoding='utf-8') as file:
        data = json.load(file) 
        zeitungen = data['newspapers']
        return zeitungen

zeitungen =importNewspapers()

st.title("Die Schlagzeile von Morgen")

zeitung_names = [zeitung['Name'] for zeitung in zeitungen]
ausgewählteZeitung = st.selectbox('Von welcher Zeitung willst du lesen?', zeitung_names, index=2)

ausgewählteZeitung = next(zeitung for zeitung in zeitungen if zeitung['Name'] == ausgewählteZeitung)

systemPrompt = f"Du bist Redaktuer der Zeitung {ausgewählteZeitung['Name']} in einem planspiel. Du schreibst texte über das aktuelle geschehen im Planspiel. Ziel ist es möglichst extreme und kontroverse Szenarien zu entwerfen. Dabei soll der Leser emotional angesprochen und aufgewühlt werden. Die Zeitung heißt {ausgewählteZeitung['Name']} und operiert unter dem Motto: {ausgewählteZeitung['Motto']}  {ausgewählteZeitung['Hintergrund']} Die Stilvorgabe lautet: {ausgewählteZeitung["Stil"]}"
st.markdown(systemPrompt)
systemMessage = [{"role": "system","content": systemPrompt}]

if prompt := st.chat_input("Zu welchem Medienereigniss willst du Informationen?"):
    st.write("You:<br>" + prompt, unsafe_allow_html=True)

    combined_prompt = systemMessage + [{"role": "user", "content": prompt}]

    response = ollama.chat(model=modelID, messages=combined_prompt)
    st.write("Model:<br>" +  str (response.message.content), unsafe_allow_html=True)