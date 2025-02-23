import streamlit as st
from streamlit_echarts import st_echarts
from streamlit_chat import message  # Für den Chatbot (streamlit-chat installieren)
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("Wahlprogramm und Bundestag - Vergleich")

# Wordcloud
st.subheader("Wordcloud")

import functions as f

combined_data = f.merge_party_json_files("Data/wahlprogramm_topics")

combined_wordcloud = f.create_wordcloud(combined_data, 100)

st_echarts(combined_wordcloud, height="400px")

# Navigation
st.subheader("Navigation")

party_to_page = {
    "BSW": "bsw",
    "SPD": "spd",
    "CDU_CSU": "cducu",
    "BÜNDNIS 90_DIE GRÜNEN": "gruene",
    "FDP": "fdp",
    "DIE LINKE": "dielinke",
    "AfD": "afd"
}

cols = st.columns(len(party_to_page))
for col, (party, page) in zip(cols, party_to_page.items()):
    col.markdown(
        f"<a href='/{page}' target='_self'><button style='width:100%; padding:10px;'>{party}</button></a>",
        unsafe_allow_html=True
    )


# Chatbot
st.subheader("Chatbot")

