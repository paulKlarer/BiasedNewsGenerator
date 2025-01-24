import streamlit as st
import ollama 
import helper.constants as constants
import helper.data.importFunctions as read
import numpy as np

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

def find_top_n_chunks(question_embedding, chunk_embeddings, top_n=3):
    # Calculate cosine similarities manually
    similarities = [cosine_similarity(question_embedding, chunk_embedding) for chunk_embedding in chunk_embeddings]
    
    # Get the indices of the top N chunks with the highest cosine similarities
    top_n_indices = np.argsort(similarities)[-top_n:][::-1]
    
    # Return the indices and corresponding similarity scores
    top_n_chunks = [(idx, similarities[idx]) for idx in top_n_indices]
    return top_n_chunks

def convert_to_llm_conversation(question: str, top_chunks: list[str]):
    messages = []
    chunks = "\n\n".join([x[0] for x in top_chunks])
    content = f""""Schreib in dem vorgegeben Still jeweils einen Artikel zu folgenden {themen} Nutze dafür fdiese Hintegrundinforamtionen\n{chunks}\n\n{question}"""
    messages.append({"role": "user", "content": content})
    
    return messages

st.title("Die Schlagzeile von Morgen")

zeitung_names = [zeitung['Name'] for zeitung in zeitungen]
ausgewählteZeitung = st.selectbox('Von welcher Zeitung willst du lesen?', zeitung_names, index=2)

ausgewählteZeitung = next(zeitung for zeitung in zeitungen if zeitung['Name'] == ausgewählteZeitung)

themen = read.themen(ausgewählteZeitung['Name'])
homepage = read.homepage()

#chunk context
homepage_chunks = chunk_text(homepage)
#embed context
chunk_embeddings = ollama.embed(model=embed_model, input=homepage_chunks)["embeddings"]
#emdeb questions
topic_embeddings = ollama.embed(model=embed_model, input=themen)["embeddings"]
#find matching chunks
matching_chunks = []

for i, question_embedding in enumerate(topic_embeddings):
        top_n_chunks = find_top_n_chunks(question_embedding, chunk_embeddings)
        matching_chunks.append({
            'question': topic_embeddings[i],
            'top_chunks': [(homepage_chunks[idx], similarity) for idx, similarity in top_n_chunks]
        })
        
#build prompt
systemPrompt = f"Du bist Redaktuer der Zeitung {ausgewählteZeitung['Name']} in einem planspiel. Du schreibst texte über das aktuelle geschehen im Planspiel. Ziel ist es möglichst extreme und kontroverse Szenarien zu entwerfen. Dabei soll der Leser emotional angesprochen und aufgewühlt werden. Die Zeitung heißt {ausgewählteZeitung['Name']} und operiert unter dem Motto: {ausgewählteZeitung['Motto']}  {ausgewählteZeitung['Hintergrund']} Die Stilvorgabe lautet: {ausgewählteZeitung["Stil"]}."
systemMessage = [{"role": "system","content": systemPrompt}]

combined_prompt = systemMessage + convert_to_llm_conversation(themen,matching_chunks)
st.write("Propmt:<br>" +  str(combined_prompt), unsafe_allow_html=True )
response = ollama.chat(model=modelID, messages=combined_prompt)
st.write("Model:<br>" +  str (response.message.content), unsafe_allow_html=True)