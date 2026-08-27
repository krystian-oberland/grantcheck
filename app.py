import json
from pathlib import Path

import pandas as pd
import streamlit as st

from exporter import build_grants_excel
from matcher import STATUS_MATCH, STATUS_REVIEW, evaluate_match

BASE_DIR = Path(__file__).parent

STATUS_DISPLAY = {
    STATUS_MATCH: st.success,
    STATUS_REVIEW: st.warning,
}


def load_json(filename):
    with open(BASE_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


def show_match_result(result):
    display_fn = STATUS_DISPLAY.get(result["status"], st.error)
    display_fn(f"{result['status']} – wynik dopasowania: {result['score']}%")

    st.write("**Uzasadnienie:**")
    for reason in result["reasons"]:
        st.write(f"- {reason}")

    if result["missing_info"]:
        st.write("**Brakujące informacje:**")
        for item in result["missing_info"]:
            st.write(f"- {item}")


def build_summary_rows(foundation, grants):
    rows = []
    for g in grants:
        result = evaluate_match(foundation, g)
        rows.append(
            {
                "Konkurs": g["title"],
                "Termin": g["deadline"],
                "Kwota": g["amount"],
                "Wynik (%)": result["score"],
                "Status": result["status"],
                "Najważniejsze uzasadnienie": result["reasons"][0] if result["reasons"] else "",
                "Link": g["url"],
            }
        )
    return rows


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

if st.button("Oceń dopasowanie"):
    show_match_result(evaluate_match(foundation, grant))

st.header("Zestawienie wszystkich konkursów")
st.write(f"Ocena dopasowania wszystkich konkursów do: **{foundation['name']}**")

summary_rows = build_summary_rows(foundation, grants)
summary_df = pd.DataFrame(summary_rows)
st.dataframe(summary_df, use_container_width=True)

excel_bytes = build_grants_excel(summary_rows)
st.download_button(
    "Pobierz wyniki do Excela",
    data=excel_bytes,
    file_name="zestawienie_konkursow.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
