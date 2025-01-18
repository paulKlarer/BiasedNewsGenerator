import streamlit as st
import ollama 
import helper.constants as constants
import helper.data.importFunctions as read

modelID = constants.MODEL_ID

zeitungen =read.newspapers()

st.title("Die Schlagzeile von Morgen")

zeitung_names = [zeitung['Name'] for zeitung in zeitungen]
ausgewählteZeitung = st.selectbox('Von welcher Zeitung willst du lesen?', zeitung_names, index=2)

ausgewählteZeitung = next(zeitung for zeitung in zeitungen if zeitung['Name'] == ausgewählteZeitung)

themen = read.themen(ausgewählteZeitung['Name'])
homepage = read.homepage()

systemPrompt = f"Du bist Redaktuer der Zeitung {ausgewählteZeitung['Name']} in einem planspiel. Du schreibst texte über das aktuelle geschehen im Planspiel. Ziel ist es möglichst extreme und kontroverse Szenarien zu entwerfen. Dabei soll der Leser emotional angesprochen und aufgewühlt werden. Die Zeitung heißt {ausgewählteZeitung['Name']} und operiert unter dem Motto: {ausgewählteZeitung['Motto']}  {ausgewählteZeitung['Hintergrund']} Die Stilvorgabe lautet: {ausgewählteZeitung["Stil"]}."

systemMessage = [{"role": "system","content": systemPrompt}]

prompt = f"Schreib in dem vorgegeben Still jeweil einen Artikel zu folgenden {themen}. Nutze dafür diese Hintergrundinformationen {homepage}."

combined_prompt = systemMessage + [{"role": "user", "content": prompt}]
st.write("Propmt:<br>" +  str(combined_prompt), unsafe_allow_html=True )
response = ollama.chat(model=modelID, messages=combined_prompt)
st.write("Model:<br>" +  str (response.message.content), unsafe_allow_html=True)