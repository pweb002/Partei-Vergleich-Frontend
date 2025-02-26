import streamlit as st
import functions as f

st.set_page_config(layout="wide")

# **Liste der Parteien**
parties = {
    "AfD": "AfD",
    "BSW": "BSW",
    "CDU / CSU": "CDU_CSU",
    "Die Linke": "DIE LINKE",
    "FDP": "FDP",
    "Die Grünen": "BÜNDNIS 90_DIE GRÜNEN",
    "SPD": "SPD"
}

selected_party = st.radio("Wähle eine Partei:", list(parties.keys()))

max_topics = st.slider("Maximale Anzahl von Themen:", min_value=5, max_value=50, value=20, step=1)

f.render_party_page(parties[selected_party], max_topics)
