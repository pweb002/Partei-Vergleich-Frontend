import json
import glob
import os
import streamlit as st
from streamlit_echarts import st_echarts

def get_party_color(party):
    """
    Gibt die RGB-Farbe einer Partei zurück.
    """
    party_colors = {
        "FDP": "rgb(243, 212, 59)", 
        "SPD": "rgb(248, 74, 95)",  
        "CDU/CSU": "rgb(154, 161, 182)",  
        "BÜNDNIS 90/DIE GRÜNEN": "rgb(91, 167, 0)",  
        "BSW": "rgb(168, 100, 255)",  
        "AfD": "rgb(55, 167, 228)",  
        "DIE LINKE": "rgb(219, 51, 169)"  
    }
    return party_colors.get(party, "rgb(255,255,255)")  # Standard: weiß, falls Partei nicht gefunden wird


def merge_party_json_files(json_folder: str):
    """
    Liest alle JSON-Dateien aus einem Ordner, extrahiert die 'topics' und speichert sie mit neuen IDs zusammengeführt ab.
    Zusätzlich wird die 'party'-Information aus der Datei übernommen.

    :param json_folder: Pfad zum Ordner, der die JSON-Dateien enthält.
    :param output_file: Pfad zur Ausgabedatei.
    """
    json_files = glob.glob(os.path.join(json_folder, "*.json"))

    combined_topics = []
    current_id = 0

    for file in json_files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

            party = data.get("party", "Unbekannt")

            if "topics" in data:
                for topic in data["topics"]:
                    topic["id"] = current_id
                    topic["party"] = party
                    combined_topics.append(topic)
                    current_id += 1

    output_data = {"topics": combined_topics}

    return output_data


def load_party_data(party, folder):
    """Lädt die JSON-Datei der Partei"""
    file_path = f"{folder}/{party}_topics.json"
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_wordcloud_data(data, max_topics):
    """Erstellt die Wordcloud-Daten aus den Partei JSON Daten.

    :param data: JSON-Daten mit Topics.
    :param max_topics: Maximale Anzahl an Topics, die ausgegeben werden sollen.
    :return: party_topics: Liste mit den Topics für die Wordcloud.
    """
    if not data:
        return [], [], "gray"  # Rückfallfarbe, falls keine Daten vorhanden sind

    all_topics = []
    party_topics = []

    # Prüfe, ob eine allgemeine "party"-Angabe existiert
    general_party = data.get("party", None)
    color = get_party_color(general_party) if general_party else "gray"

    # Durch die Themen iterieren und Wordcloud-Daten erstellen
    topics = data.get("topics")

    # Falls `max_topics` gesetzt ist, limitieren wir die Anzahl der Themen
    if max_topics is not None:
        topics = topics[:max_topics]  # Begrenze die Anzahl der Topics

    for topic in topics:
        topic_party = topic.get("party", general_party)  # Falls keine Party im Topic, nimm die allgemeine
        topic_color = get_party_color(topic_party) if topic_party else color  # Falls keine Farbe gefunden, Standard nehmen

        topic_words = topic.get("words", [])

        all_topics.append(topic_words)

        party_topics.append({
            "name": topic_words[0],
            "value": topic.get("count", 1),
            "textStyle": {"color": topic_color},
            "tooltip": {
                "formatter": f"""{topic_party}<br/><br/>
                                Thema Erwähnungen: {topic.get('count', 1)}<br/><br/>
                                Zugehörige Wörter:<br/>{"<br/>".join(f"- {word}" for word in topic_words)}"""
            }
        })

    return party_topics


def create_wordcloud(data, max_topics=20):
    """Erstellt die Optionen für die Wordcloud"""
    main_topics = build_wordcloud_data(data, max_topics)

    return {
        "tooltip": {
            "show": True,
        },
        "series": [{
            "type": "wordCloud",
            "data": main_topics,
            "drawOutOfBound": True,
            "emphasis": {
                "focus": "self",
                "textStyle": {
                    "textShadowBlur": 10,
                    "textShadowColor": "#333"
                }
            },
            "gridSize": 2,
            "sizeRange": [12, 60],
            "rotationRange": [-90, 90],
            "shape": "circle",
            "width": "100%",
            "shrinkToFit": True,
            "layoutAnimation": True
        }]
    }


def load_party_analysis(party, filename="Data/Ausgaben.json"):
    """Lädt die JSON-Datei mit den Parteiauswertungen."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data.get(party, {})
    except FileNotFoundError:
        st.error(f"Fehler: Datei {filename} nicht gefunden.")
        return {}
    except json.JSONDecodeError:
        st.error(f"Fehler: Datei {filename} enthält ungültiges JSON.")
        return {}

def render_party_page(party, max_topics = 20):
    """Zeigt die Parteianalyse mit den Themen und Bewertungen an."""

    # Lade Daten der Partei
    wahlprogramm_data = load_party_data(party, "Data/wahlprogramm_topics")
    plenarsitzung_data = load_party_data(party, "Data/plenarsitzung_topics")
    parteianalyse_data = load_party_analysis(party)

    if not wahlprogramm_data:
        st.error(f"Keine Daten für Partei {party} gefunden.")
        return

    st.title(f"Themen der Partei {wahlprogramm_data['party']}")

    # Wordclouds
    wahlprogramm_wordcloud = create_wordcloud(wahlprogramm_data, max_topics)
    plenarsitzung_wordcloud = create_wordcloud(plenarsitzung_data, max_topics)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Wahlprogramm")
        st_echarts(wahlprogramm_wordcloud, height="1000px", key=f"{party}_wahlprogramm")

    with col2:
        st.subheader("Plenarsitzung")
        st_echarts(plenarsitzung_wordcloud, height="1000px", key=f"{party}_plenarsitzung")

    # Themenübersicht mit Analyse
    st.subheader("Themenübersicht des Wahlprogrammes")
    for topic in wahlprogramm_data["topics"]:
        topic_words = ", ".join(topic["words"])
        topic_analysis = parteianalyse_data.get(topic_words, "Keine Analyse verfügbar.")

        with st.expander(f"Topic {topic['id']} - {topic_words}"):
            st.write(f"**Wichtige Begriffe:** {topic_words}")
            st.write(f"**Erwähnungen:** {topic['count']}")
            st.markdown(f"**Analyse:**\n\n{topic_analysis}", unsafe_allow_html=True)

    

