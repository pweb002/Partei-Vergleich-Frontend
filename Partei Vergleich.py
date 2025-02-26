import streamlit as st
from streamlit_echarts import st_echarts
from streamlit_chat import message 
import streamlit.components.v1 as components
import functions as f

st.set_page_config(layout="wide")

st.title("Wahlprogramm und Bundestag - Vergleich")

max_topics = st.slider("Maximale Anzahl von Themen:", min_value=15, max_value=100, value=100, step=1)

st.subheader("Wordcloud")
combined_data = f.merge_party_json_files("Data/wahlprogramm_topics")
combined_wordcloud = f.create_wordcloud(combined_data, max_topics)
st_echarts(combined_wordcloud, height="1500%")

