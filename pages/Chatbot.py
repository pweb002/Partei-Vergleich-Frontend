import streamlit as st
import requests
import json
import torch
import chromadb
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
import os

st.set_page_config(layout="centered")

os.environ["CUDA_VISIBLE_DEVICES"] = "1, 2, 3"

# Streamlit-UI
st.title("Politischer KI-Chatbot mit RAG")

# ChromaDB Verbindung
chroma_client = chromadb.PersistentClient(path="./Data/chromadb")
wahlprogramme_collection = chroma_client.get_or_create_collection(name="wahlprogramme")
plenarsitzungen_collection = chroma_client.get_or_create_collection(name="plenarsitzungen")

# Wähle die beste verfügbare GPU für das Embedding-Modell
def get_best_gpu():
    best_gpu = None
    max_free_mem = 0
    
    for i in range(torch.cuda.device_count()):
        free_mem = torch.cuda.memory_reserved(i) - torch.cuda.memory_allocated(i)
        if free_mem > max_free_mem:
            max_free_mem = free_mem
            best_gpu = i

    return best_gpu

best_gpu = get_best_gpu()
embedding_device = f"cuda:{best_gpu}" if best_gpu is not None else "cpu"
print(f"Embeddings werden auf GPU {best_gpu} geladen.")

# Lade Embedding-Modell auf beste GPU
embedding_model = SentenceTransformer("intfloat/multilingual-e5-large", device=embedding_device)

# Chat-Historie speichern
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Du bist ein politischer KI-Assistent, der Fakten aus offiziellen Quellen nutzt, um fundierte und prägnante Antworten zu geben."}]

# Vorherige Nachrichten anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Nutzer-Eingabe
user_input = st.chat_input("Schreibe hier deine politische Frage...")

def query_party_analysis(query):
    query_embedding = embedding_model.encode(query, normalize_embeddings=True).tolist()
    wahl_results = wahlprogramme_collection.query(query_embeddings=[query_embedding], n_results=5)
    sitzung_results = plenarsitzungen_collection.query(query_embeddings=[query_embedding], n_results=5)
    
    wahlprogramme_texts = "\n\n".join(wahl_results.get("documents", [[]])[0])
    plenarsitzungen_texts = "\n\n".join(sitzung_results.get("documents", [[]])[0])
    
    # Sende die gesammelten Informationen an Qwen für eine prägnante Antwort
    qwen_api_url = "http://localhost:8000/v1/chat/completions"
    model_name = "Qwen/Qwen2.5-1.5B-Instruct"
    prompt = f"Fasse die folgende politische Analyse kurz und verständlich zusammen:\n\n{wahlprogramme_texts}\n\n{plenarsitzungen_texts}"
    
    response = requests.post(
        qwen_api_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps({"model": model_name, "messages": [{"role": "system", "content": prompt}], "max_tokens": 256})
    )
    
    api_response = response.json()
    short_summary = api_response.get("choices", [{}])[0].get("message", {}).get("content", "Fehler: Keine Antwort erhalten")
    
    return f"**Zusammenfassung:** {short_summary}"

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    # Immer RAG verwenden mit Qwen für prägnante Antworten
    bot_response = query_party_analysis(user_input)
    
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    with st.chat_message("assistant"):
        st.write(bot_response)