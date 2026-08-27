"""Regułowa (bez AI) ocena dopasowania konkursu grantowego do profilu fundacji."""

import re

STATUS_MATCH = "Pasuje"
STATUS_REVIEW = "Do sprawdzenia"
STATUS_NO_MATCH = "Nie pasuje"

NATIONWIDE_LOCATIONS = {"cała polska", "cały kraj", "polska"}

KEYWORD_WEIGHT = 45
TARGET_GROUP_WEIGHT = 30
LOCATION_WEIGHT = 25

PASS_THRESHOLD = 65
FAIL_THRESHOLD = 20

IMPORTANT_GRANT_FIELDS = {
    "deadline": "Brak terminu składania wniosków",
    "amount": "Brak informacji o wysokości dofinansowania",
    "own_contribution": "Brak informacji o wymaganym wkładzie własnym",
    "funding_type": "Brak informacji o rodzaju finansowania",
    "locations": "Brak informacji o obszarze działania konkursu",
    "target_groups": "Brak informacji o grupach docelowych konkursu",
    "keywords": "Brak słów kluczowych konkursu",
    "url": "Brak linku do ogłoszenia",
}

# Słowa funkcyjne pomijane przy ogólnym (fallback) sprawdzaniu czerwonych flag.
_STOPWORDS = {
    "konkurs", "wymagany", "wymagane", "wymaga", "dla", "do", "od", "min",
    "status", "statusu", "wyłącznie", "lat", "posiadania", "ze", "brak",
    "możliwości",
}

_PERCENT_RE = re.compile(r"(\d+)\s*%")
_WORD_RE = re.compile(r"[a-ząćęłńóśźż]+")


def _normalize(value):
    return str(value).strip().lower()


def _normalize_list(values):
    return {_normalize(v) for v in values if v}


def _fuzzy_overlap(set_a, set_b):
    """Zwraca (elementy_a, elementy_b) dopasowane dokładnie lub przez zawieranie."""
    matched_a, matched_b = set(), set()
    for a in set_a:
        for b in set_b:
            if a == b or (len(a) > 3 and a in b) or (len(b) > 3 and b in a):
                matched_a.add(a)
                matched_b.add(b)
    return matched_a, matched_b


def _find_missing_info(grant):
    missing = []
    for field, message in IMPORTANT_GRANT_FIELDS.items():
        value = grant.get(field)
        if value in (None, "", [], {}):
            missing.append(message)
    return missing


def _evaluate_keywords(foundation, grant):
    foundation_keywords = _normalize_list(
        list(foundation.get("keywords", [])) + list(foundation.get("activities", []))
    )
    grant_keywords = _normalize_list(grant.get("keywords", []))
    if not foundation_keywords or not grant_keywords:
        return 0, None

    matched_f, matched_g = _fuzzy_overlap(foundation_keywords, grant_keywords)
    if not matched_f:
        return 0, "Brak wspólnych słów kluczowych i obszarów działania"

    ratio = len(matched_f) / len(foundation_keywords)
    points = round(min(ratio, 1.0) * KEYWORD_WEIGHT)
    sample = ", ".join(sorted(matched_g)[:4])
    return points, f"Wspólne słowa kluczowe: {sample}"


def _evaluate_target_groups(foundation, grant):
    foundation_groups = _normalize_list(foundation.get("target_groups", []))
    grant_groups = _normalize_list(grant.get("target_groups", []))
    if not foundation_groups or not grant_groups:
        return 0, None

    matched_f, matched_g = _fuzzy_overlap(foundation_groups, grant_groups)
    if not matched_f:
        return 0, "Brak wspólnych grup docelowych"

    ratio = len(matched_f) / len(foundation_groups)
    points = round(min(ratio, 1.0) * TARGET_GROUP_WEIGHT)
    sample = ", ".join(sorted(matched_g)[:3])
    return points, f"Wspólne grupy docelowe: {sample}"


def _evaluate_location(foundation, grant):
    foundation_locations = _normalize_list(foundation.get("locations", []))
    grant_locations = _normalize_list(grant.get("locations", []))
    if not grant_locations:
        return 0, None

    if grant_locations & NATIONWIDE_LOCATIONS:
        return LOCATION_WEIGHT, "Konkurs ogólnopolski – otwarty również dla lokalizacji fundacji"

    matched_f, matched_g = _fuzzy_overlap(foundation_locations, grant_locations)
    if matched_f:
        sample = ", ".join(sorted(matched_g))
        return LOCATION_WEIGHT, f"Zgodność lokalizacji: {sample}"

    return 0, "Lokalizacja konkursu nie pokrywa się z lokalizacją fundacji"


def _check_contribution_red_flag(red_flag_text, grant):
    if "wkład własny" not in red_flag_text:
        return None
    threshold_match = _PERCENT_RE.search(red_flag_text)
    if not threshold_match:
        return None
    threshold = int(threshold_match.group(1))

    grant_match = _PERCENT_RE.search(grant.get("own_contribution") or "")
    if not grant_match:
        return None
    grant_percent = int(grant_match.group(1))

    if grant_percent > threshold:
        return {
            "severity": "hard",
            "reason": (
                f"Wymagany wkład własny ({grant_percent}%) przekracza "
                f"próg fundacji ({threshold}%)"
            ),
        }
    return None


def _check_exclusive_target_red_flag(red_flag_text, grant):
    if "wyłącznie dla" not in red_flag_text and "wyłącznie do" not in red_flag_text:
        return None

    grant_targets = grant.get("target_groups") or []
    if len(grant_targets) != 1:
        return None

    only_target = _normalize(grant_targets[0])
    target_words = [w for w in _WORD_RE.findall(only_target) if len(w) > 4]
    if not target_words:
        return None

    flag_lower = red_flag_text.lower()
    matches = sum(1 for w in target_words if w in flag_lower)
    if matches >= max(1, len(target_words) - 1):
        return {
            "severity": "hard",
            "reason": (
                "Konkurs skierowany wyłącznie do grupy niezgodnej z profilem "
                f"fundacji ({grant_targets[0]})"
            ),
        }
    return None


def _check_generic_red_flag(red_flag_text, grant):
    text_pool = " ".join(
        [
            grant.get("title", ""),
            grant.get("description", ""),
            " ".join(grant.get("keywords", [])),
        ]
    ).lower()

    words = [
        w for w in _WORD_RE.findall(red_flag_text.lower())
        if w not in _STOPWORDS and len(w) > 3
    ]
    hits = [w for w in words if w in text_pool]
    if hits:
        return {
            "severity": "soft",
            "reason": f"Możliwa niezgodność z zastrzeżeniem fundacji: „{red_flag_text}”",
        }
    return None


def evaluate_match(foundation, grant):
    """Oceń dopasowanie pojedynczego konkursu (`grant`) do profilu `foundation`.

    Zwraca słownik: {"score": 0-100, "status": str, "reasons": [...], "missing_info": [...]}.
    """
    reasons = []
    missing_info = _find_missing_info(grant)
    if missing_info:
        reasons.append("Brakujące informacje: " + "; ".join(missing_info))

    keyword_points, keyword_reason = _evaluate_keywords(foundation, grant)
    target_points, target_reason = _evaluate_target_groups(foundation, grant)
    location_points, location_reason = _evaluate_location(foundation, grant)

    for reason in (keyword_reason, target_reason, location_reason):
        if reason:
            reasons.append(reason)

    score = keyword_points + target_points + location_points

    hard_red_flag = False
    soft_red_flag = False
    for red_flag_text in foundation.get("red_flags", []):
        result = (
            _check_contribution_red_flag(red_flag_text, grant)
            or _check_exclusive_target_red_flag(red_flag_text, grant)
            or _check_generic_red_flag(red_flag_text, grant)
        )
        if result:
            reasons.append(result["reason"])
            if result["severity"] == "hard":
                hard_red_flag = True
                score -= 40
            else:
                soft_red_flag = True
                score -= 10

    score -= 5 * len(missing_info)
    score = max(0, min(100, score))

    # Brak jakiegokolwiek pokrycia tematycznego i grupowego to jednoznaczny brak
    # dopasowania, nawet jeśli konkurs jest ogólnopolski (co samo w sobie dawałoby punkty).
    no_real_overlap = keyword_points == 0 and target_points == 0

    if hard_red_flag or no_real_overlap:
        status = STATUS_NO_MATCH
        score = min(score, FAIL_THRESHOLD)
    elif score >= PASS_THRESHOLD and not soft_red_flag and not missing_info:
        status = STATUS_MATCH
    elif score <= FAIL_THRESHOLD:
        status = STATUS_NO_MATCH
    else:
        # Przypadek niejednoznaczny – lepiej pokazać niepewny wynik niż pominąć konkurs.
        status = STATUS_REVIEW

    if not reasons:
        reasons.append("Brak istotnych sygnałów dopasowania")

    return {
        "score": score,
        "status": status,
        "reasons": reasons,
        "missing_info": missing_info,
    }
