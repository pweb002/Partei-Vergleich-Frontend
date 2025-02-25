import streamlit as st
from streamlit_echarts import st_echarts
from streamlit_chat import message 
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("Wahlprogramm und Bundestag - Vergleich")

# Wordcloud
st.subheader("Wordcloud")

import functions as f

combined_data = f.merge_party_json_files("Data/wahlprogramm_topics")

combined_wordcloud = f.create_wordcloud(combined_data, 100)

st_echarts(combined_wordcloud, height="1500%")

