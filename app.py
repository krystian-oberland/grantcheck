import json
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).parent


def load_json(filename):
    with open(BASE_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


st.title("GrantCheck Mini")
st.write("Wstępna ocena dopasowania konkursów grantowych do profilu fundacji.")
st.info("To jest wersja demonstracyjna aplikacji.")

foundations = load_json("foundations.json")
grants = load_json("demo_grants.json")

st.header("Profil fundacji")
foundation_names = [f["name"] for f in foundations]
selected_foundation_name = st.selectbox("Wybierz fundację", foundation_names)
foundation = next(f for f in foundations if f["name"] == selected_foundation_name)

st.subheader(foundation["name"])
st.write(f"**Lokalizacje:** {', '.join(foundation['locations'])}")
st.write(f"**Obszary działania:** {', '.join(foundation['activities'])}")
st.write(f"**Grupy docelowe:** {', '.join(foundation['target_groups'])}")
st.write(f"**Słowa kluczowe:** {', '.join(foundation['keywords'])}")
st.write(f"**Red flagi:** {', '.join(foundation['red_flags'])}")

st.header("Konkurs grantowy")
grant_titles = [g["title"] for g in grants]
selected_grant_title = st.selectbox("Wybierz konkurs", grant_titles)
grant = next(g for g in grants if g["title"] == selected_grant_title)

st.subheader(grant["title"])
st.write(f"**Organizator:** {grant['organizer']}")
st.write(f"**Termin składania wniosków:** {grant['deadline']}")
st.write(f"**Kwota dofinansowania:** {grant['amount']}")
st.write(f"**Wkład własny:** {grant['own_contribution']}")
st.write(f"**Rodzaj finansowania:** {grant['funding_type']}")
st.write(f"**Lokalizacje:** {', '.join(grant['locations'])}")
st.write(f"**Grupy docelowe:** {', '.join(grant['target_groups'])}")
st.write(f"**Słowa kluczowe:** {', '.join(grant['keywords'])}")
st.write(f"**Opis:** {grant['description']}")
st.write(f"**Link:** {grant['url']}")
