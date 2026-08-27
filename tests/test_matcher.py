import json
from pathlib import Path

from matcher import STATUS_MATCH, STATUS_NO_MATCH, evaluate_match

BASE_DIR = Path(__file__).parent.parent


def load_json(filename):
    with open(BASE_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


FOUNDATIONS = {f["id"]: f for f in load_json("foundations.json")}
GRANTS = {g["id"]: g for g in load_json("demo_grants.json")}


def test_dobrze_dopasowany_konkurs_do_pro_fil():
    foundation = FOUNDATIONS["pro-fil"]
    grant = GRANTS["g1"]  # program przeciwdziałania przemocy w podkarpackiem

    result = evaluate_match(foundation, grant)

    assert result["status"] == STATUS_MATCH
    assert result["score"] >= 65
    assert result["reasons"]
    assert result["missing_info"] == []


def test_dobrze_dopasowany_konkurs_do_pociechom():
    foundation = FOUNDATIONS["pociechom"]
    grant = GRANTS["g3"]  # hipoterapia/alpakoterapia dla dzieci z niepełnosprawnościami

    result = evaluate_match(foundation, grant)

    assert result["status"] == STATUS_MATCH
    assert result["score"] >= 65
    assert result["reasons"]
    assert result["missing_info"] == []


def test_konkurs_niedopasowany_do_zadnej_fundacji():
    grant = GRANTS["g6"]  # czyste powietrze dla gmin – bez związku z żadną fundacją

    for foundation in FOUNDATIONS.values():
        result = evaluate_match(foundation, grant)
        assert result["status"] == STATUS_NO_MATCH
        assert result["score"] <= 20
