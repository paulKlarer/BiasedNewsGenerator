import streamlit as st
import ollama 

MODEL_ID = 'llama3.1:8b-instruct-q4_0'

Zeitungen = ['Volksstimme', 'Der Aufbruch', 'Klartext', 'Der Kritische Beobachter']
Zeitungsmottos = {
    'Volksstimme': 'Ein Volk, Eine Wahrhiet, Eine Zeitung',
    'Der Aufbruch': 'Für ein neues Zeitalter der Gerechtigkeit',
    'Klartext' : 'Der unabhängige Blick',
    'Der Kritische Beobachter': 'Für unabhängigen Journalismus'
}

st.markdown(f"### Prompt: ``{MODEL_ID}``")
ausgewählteZeitung = st.selectbox('Von welcher Zeitung willst du lesen?',Zeitungsmottos,index =2)

if prompt := st.chat_input("Zu welchem Medienereigniss willst du Informationen?"):
    st.write("You:<br>" + prompt, unsafe_allow_html=True)
    response = ollama.generate(model=MODEL_ID, prompt=prompt)
    st.write("Model:<br>" + response["response"], unsafe_allow_html=True)
