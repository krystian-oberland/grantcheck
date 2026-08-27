"""Eksport zestawienia ocenionych konkursów do pliku Excel (w pamięci)."""

from io import BytesIO

import pandas as pd


def build_grants_excel(rows):
    """Zbuduj plik .xlsx z zestawieniem konkursów.

    `rows` to lista słowników, np. z kolumnami:
    Konkurs, Termin, Kwota, Wynik (%), Status, Uzasadnienie, Link.
    Zwraca zawartość pliku Excel jako bytes, gotową do pobrania w Streamlit.
    """
    df = pd.DataFrame(rows)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Zestawienie konkursów")
    return buffer.getvalue()
