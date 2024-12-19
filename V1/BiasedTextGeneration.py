import streamlit as st
import ollama 

modelID ='mannix/llama3.1-8b-abliterated'

zeitungen = [
    {
        'Name': 'Volksstimme',
        'Motto': 'Ein Volk, Eine Wahrheit, Eine Zeitung',
        'Hintergrund': '. Schreibe aus nationalistischer Perspektive, betone die Einheit des Volkes und die Bedeutung des Führers.Schüre Ängste vor Fremden und Neuerungen. Die wichtigsten politischen Themen sind Nationalismus, Patriotismus und Überfremdung durch unkontrollierte Migration. Der Text soll reißerisch und populistisch formuliert sein. Ziel des Textes ist es Wut und Angst zu schüren'
    },
    {
        'Name': 'Der Aufbruch',
        'Motto': 'Für ein neues Zeitalter der Gerechtigkeit',
        'Hintergrund': '. Verwende eine revolutionäre Sprache, fordere soziale Gerechtigkeit und einen Umsturz des bestehenden Systems. Kritisiere das Establishment scharf für seine Ausbeutung der Menschen und des Planeten. Die wichtigsten politischen Themen sind Sozialismus, Verarmung und der Kampf gegen den Klimawandel. Der Text soll reißerisch formuliert sein.'
    },
    {
        'Name': 'Klartext',
        'Motto': 'Der unabhängige Blick',
        'Hintergrund': '. Recherchiere gründlich und präsentiere Fakten objektiv. Vermeide jegliche Parteilichkeit. Die wichtigsten politischen Themen sind die Stärkung der Wirtschaft, Klimawandel und eine Stärkung der EU und NATO. Der Text soll überzeugend, aber seriös sein.'
    },
    {
        'Name': 'Der Kritische Beobachter',
        'Motto': 'Regierungstreue ist die Erste Bürgerpflicht',
        'Hintergrund': '. Unterstütze die Regierung bedingungslos und kritisiere jegliche Opposition. Betone die Wichtigkeit von Stabilität und Ordnung. Wenn man die Regierung nicht destabilisiert und ihren Job machen lässt, wird alles gut. Die Fokuspunkte der Regierung sind die wichtigsten Themen. Der Text soll überzeugend, aber seriös sein.'
    }
]


st.title("Die Schlagzeile von Morgen")

zeitung_names = [zeitung['Name'] for zeitung in zeitungen]
ausgewählteZeitung = st.selectbox('Von welcher Zeitung willst du lesen?', zeitung_names, index=2)

ausgewählteZeitung = next(zeitung for zeitung in zeitungen if zeitung['Name'] == ausgewählteZeitung)

systemPrompt = f"Du bist Redaktuer der Zeitung {ausgewählteZeitung['Name']} in einem planspiel. Du schreibst texte über das aktuelle geschehen im Planspiel. Ziel ist es möglichst extreme und kontroverse Szenarien zu entwerfen. Dabei soll der Leser emotional angesprochen und aufgewühlt werden. Die Zeitung heißt {ausgewählteZeitung['Name']} und operiert unter dem Motto: {ausgewählteZeitung['Motto']}  {ausgewählteZeitung['Hintergrund']}"
st.markdown(systemPrompt)
systemMessage = [{"role": "system","content": systemPrompt}]

if prompt := st.chat_input("Zu welchem Medienereigniss willst du Informationen?"):
    st.write("You:<br>" + prompt, unsafe_allow_html=True)

    combined_prompt = systemMessage + [{"role": "user", "content": prompt}]

    response = ollama.chat(model=modelID, messages=combined_prompt)
    st.write("Model:<br>" +  str (response.message.content), unsafe_allow_html=True)