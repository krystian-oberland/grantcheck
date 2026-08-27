# GrantCheck Mini

GrantCheck Mini to prosta aplikacja w Pythonie i Streamlit, która wspiera wstępną ocenę dopasowania konkursów grantowych do profilu fundacji.

## Jaki problem rozwiązuje

Organizacje pozarządowe muszą na bieżąco przeglądać wiele ogłoszeń o konkursach grantowych i ręcznie oceniać, czy dany konkurs w ogóle pasuje do ich profilu (obszar działania, grupa docelowa, lokalizacja, warunki finansowe). Jest to czasochłonne i łatwo przy tym przeoczyć istotny konkurs albo stracić czas na analizę oferty, która od razu odpada. GrantCheck Mini automatyzuje ten wstępny etap selekcji, dzięki czemu użytkownik szybciej widzi, które konkursy warto przeanalizować dokładniej.

## Funkcje obecnego MVP

- wybór profilu fundacji z listy,
- wybór konkursu grantowego z listy i podgląd jego szczegółów,
- regułowa (bez AI) ocena dopasowania wybranego konkursu do wybranej fundacji,
- zestawienie wszystkich konkursów wraz z wynikiem dopasowania dla wybranej fundacji,
- eksport zestawienia wyników do pliku Excel,
- podstawowe testy automatyczne logiki oceniającej.

## Dane demonstracyjne

Profile fundacji (`foundations.json`) oraz konkursy grantowe (`demo_grants.json`) są danymi **demonstracyjnymi i fikcyjnymi**, przygotowanymi wyłącznie na potrzeby prezentacji działania aplikacji. Nie należy traktować ich jako rzeczywistych ofert grantowych.

## Sposób oceniania

Ocena dopasowania konkursu do profilu fundacji jest w pełni regułowa (bez udziału AI) i uwzględnia:

- **wspólne słowa kluczowe** – porównanie obszarów działania i słów kluczowych fundacji ze słowami kluczowymi konkursu,
- **wspólne grupy docelowe** – porównanie grup docelowych fundacji i konkursu,
- **zgodność lokalizacji** – czy konkurs obejmuje obszar działania fundacji (w tym konkursy ogólnopolskie),
- **czerwone flagi** – sprawdzenie warunków, które mogą wykluczać fundację (np. zbyt wysoki wymagany wkład własny, konkurs skierowany wyłącznie do innego typu podmiotów),
- **brakujące ważne informacje** – sygnalizacja, gdy w opisie konkursu brakuje istotnych danych (np. terminu, kwoty czy wkładu własnego).

Wynik to ocena punktowa od 0 do 100 oraz jeden z trzech statusów: „Pasuje”, „Do sprawdzenia” lub „Nie pasuje”. W przypadkach niejednoznacznych aplikacja celowo wybiera status „Do sprawdzenia” — pominięcie potencjalnie pasującego konkursu jest gorsze niż pokazanie niepewnego wyniku.

## Uruchomienie lokalne (Windows / PowerShell)

```powershell
# utworzenie środowiska wirtualnego
python -m venv .venv

# aktywacja środowiska w PowerShell
.venv\Scripts\Activate.ps1

# instalacja zależności
pip install -r requirements.txt

# uruchomienie aplikacji
streamlit run app.py
```

## Uruchomienie testów

```powershell
pytest
```

## Użyte technologie

- Python
- Streamlit
- Pydantic
- Pandas
- openpyxl
- pytest

## Możliwe dalsze kroki

- automatyczne monitorowanie stron internetowych z ogłoszeniami o konkursach,
- odczyt i analiza treści ogłoszeń w plikach PDF,
- wsparcie modeli AI przy ocenie dopasowania i podsumowywaniu ogłoszeń,
- harmonogram przypominający o zbliżających się terminach,
- powiadomienia o nowych, pasujących konkursach.

## Ostrzeżenie

GrantCheck Mini dostarcza wyłącznie wstępną, orientacyjną ocenę dopasowania. Ostateczną decyzję o udziale w konkursie i szczegółową weryfikację warunków zawsze powinien wykonać człowiek.
