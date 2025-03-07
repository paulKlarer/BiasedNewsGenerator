import streamlit as st
import ollama 
import helper.constants as constants
import helper.data.importFunctions as read
import numpy as np
import json

modelID = constants.MODEL_ID
embed_model = constants.EMBED_MODEL_ID

zeitungen =read.newspapers()

# Function to chunk the extracted text
def chunk_text(text: str, chunk_size=500):
    # Split text into chunks of specified size
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def cosine_similarity(vec1, vec2):
    # Compute dot product
    dot_product = np.dot(vec1, vec2)
    
    # Compute magnitude of the vectors
    magnitude_vec1 = np.sqrt(np.dot(vec1, vec1))
    magnitude_vec2 = np.sqrt(np.dot(vec2, vec2))
    
    # Avoid division by zero in case of zero vectors
    if magnitude_vec1 == 0 or magnitude_vec2 == 0:
        return 0.0
    
    # Compute cosine similarity
    cosine_similarity = dot_product / (magnitude_vec1 * magnitude_vec2)
    return cosine_similarity

def find_top_n_chunks(question_embedding, chunk_embeddings, top_n=1):
    # Calculate cosine similarities manually
    similarities = [cosine_similarity(question_embedding, chunk_embedding) for chunk_embedding in chunk_embeddings]
    
    # Get the indices of the top N chunks with the highest cosine similarities
    top_n_indices = np.argsort(similarities)[-top_n:][::-1]
    
    # Return the indices and corresponding similarity scores
    top_n_chunks = [(idx, similarities[idx]) for idx in top_n_indices]
    return top_n_chunks

def convert_to_llm_conversation(question: str, top_chunks: list[tuple]):
    messages = []
    # Joining text from the given tuples directly
    chunks = "\n\n".join([str(chunk) for chunk, _ in top_chunks])
    content = f""" Nutze  diese Hintergrundinformationen:\n{chunks}\n\n Um einen Artikel zu folgenden Thema zu schreiben {question} Halte dich an die Stil- und Mottovorgaben der Zeitung."""
    messages.append({"role": "user", "content": content})

    return messages

def convert_unicode_escapes(text):
    return text.encode('iso-8859-1').decode('unicode_escape')

st.title("Die Schlagzeile von Morgen")

zeitung_names = [zeitung['Name'] for zeitung in zeitungen]
ausgewählteZeitung = st.selectbox('Von welcher Zeitung willst du lesen?', zeitung_names, index=0)

ausgewählteZeitung = next(zeitung for zeitung in zeitungen if zeitung['Name'] == ausgewählteZeitung)

themen = read.themen(ausgewählteZeitung['Name'])
homepage = json.dumps(read.homepage())

#chunk and embed context
homepage_chunks = chunk_text(homepage)
chunk_embeddings = ollama.embed(model=embed_model, input=homepage_chunks)["embeddings"]

#build prompt
systemPrompt = f"Du bist Redaktuer der Boulevardzeitung {ausgewählteZeitung['Name']}. Du schreibst  Artikel über das aktuelle geschehen. Jeder Artikel hat 1 Überschrift und einen text. Ziel ist es möglichst extreme und kontroverse Szenarien zu entwerfen. Die kurzen Artikel sollen eine reiserische überschrift haben und einen Text, dieser soll der Leser emotional ansprechen  und aufwühlen. Die Zeitung heißt {ausgewählteZeitung['Name']} und operiert unter dem Motto: {ausgewählteZeitung['Motto']}  {ausgewählteZeitung['Hintergrund']} Die Stilvorgabe lautet: {ausgewählteZeitung['Stil']}."
systemMessage = [{"role": "system","content": systemPrompt}]

# Iterate over each topic to process them individually
for topic in themen:
    # Embed the current topic
    topic_embedding = ollama.embed(model=embed_model, input=[topic])["embeddings"][ 0]

    top_n_chunks = find_top_n_chunks(topic_embedding, chunk_embeddings)
    matching_chunks = convert_unicode_escapes([(homepage_chunks[idx], similarity) for idx, similarity in top_n_chunks])

    topic_conversation = convert_to_llm_conversation(topic, matching_chunks)
    combined_prompt = systemMessage + topic_conversation

    response = ollama.chat(model=modelID, messages=combined_prompt)
    model_response = convert_unicode_escapes(str(response.message.content))

    # Display the generated article
    st.write(f"Model Artikel zu +{topic}:<br>" + model_response, unsafe_allow_html=True)

