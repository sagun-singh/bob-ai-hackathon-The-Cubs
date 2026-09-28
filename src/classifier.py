"""
Classifier And Extractor
  Uses algorithm for keyword matching to classify and extract entities from FIRs.
"""

import json
import re

INPUT_FILE  = "FIR.json"
OUTPUT_FILE = "results.json"

# ======================================================================
# 1. CRIME CLASSIFIER
#    Each crime type has a list of keyword signals.
#    The type with the most keyword hits wins.
#    Order matters only as a tiebreak — more specific rules are listed first.
# ======================================================================
CRIME_RULES = [
    ("chain snatching", [
        "snatch", "snatched", "chain", "mangalsutra", "necklace",
        "gold chain", "pulled off", "neck", "jewellery", "jewelry",
    ]),
    ("cyber fraud", [
        "whatsapp", "upi", "online", "cyber", "fraud", "phishing",
        "otp", "link", "blocked", "registration fee", "work-from-home",
        "data entry", "job offer", "website", "payment", "transfer",
        "account", "qr code", "screen share",
    ]),
    ("kidnapping", [
        "kidnap", "abduct", "forcibly taken", "missing", "held captive",
        "ransom", "took away", "forcefully", "confined",
    ]),
    ("burglary", [
        "broke into", "break-in", "burglary", "burglar", "house break",
        "forced entry", "lock broken", "door broken", "window broken",
        "entered the house", "valuables stolen from home",
    ]),
    ("robbery", [
        "robbery", "robbed", "armed", "knife", "weapon", "threatened",
        "loot", "looted", "demanded", "pistol", "gun",
    ]),
    ("vehicle theft", [
        "vehicle theft", "car stolen", "bike stolen", "motorcycle stolen",
        "auto stolen", "scooter stolen", "stolen vehicle",
    ]),
    ("theft", [
        "stolen", "stole", "theft", "pickpocket", "missing wallet",
        "missing mobile", "bag snatched", "purse stolen",
    ]),
    ("assault", [
        "assault", "attacked", "beat", "beaten", "hit", "punched",
        "stabbed", "injured", "hurt", "slapped", "thrashed",
    ]),
]

def classify_crime(text: str) -> str:
    """Return the best-matching crime type based on keyword hit count."""
    text_lower = text.lower()
    scores = {}
    for crime_type, keywords in CRIME_RULES:
        hits = sum(1 for kw in keywords if kw in text_lower)
        if hits > 0:
            scores[crime_type] = hits
    if not scores:
        return "other"
    return max(scores, key=scores.get)

# ======================================================================
# 2. DATE EXTRACTOR
#    Looks for patterns like "12 March", "3 April", "On 27 March"
# ======================================================================
DATE_PATTERN = re.compile(
    r'\b(\d{1,2}(?:st|nd|rd|th)?\s+'
    r'(?:January|February|March|April|May|June|July|August|'
    r'September|October|November|December)(?:\s+\d{4})?)\b',
    re.IGNORECASE
)

def extract_date(text: str) -> str:
    match = DATE_PATTERN.search(text)
    return match.group(1).strip() if match else "unknown"

# ======================================================================
# 3. LOCATION EXTRACTOR
#    Looks for "near X", "at X", "in X", "from X", police station names,
#    and known city/area names.
# ======================================================================
LOCATION_PATTERNS = [
    # "near Sector 21 market, Gandhinagar"
    re.compile(r'\bnear\s+([\w\s,]+?)(?:\.|,\s*(?:the\s+)?complainant|complainant|\bon\b|$)', re.IGNORECASE),
    # "Registered at Navrangpura Police Station"
    re.compile(r'Registered at\s+([\w\s]+Police Station)', re.IGNORECASE),
    # "from Surat" / "in Ahmedabad"
    re.compile(r'\b(?:from|in)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b'),
    # city after a comma "Gandhinagar" / "Ahmedabad" / "Surat"
    re.compile(r',\s*([A-Z][a-z]{3,})\b'),
]

KNOWN_CITIES = {
    "gandhinagar", "ahmedabad", "surat", "vadodara", "rajkot",
    "mumbai", "delhi", "bengaluru", "hyderabad", "pune", "chennai",
    "kolkata", "jaipur", "lucknow", "bhopal", "patna",
}

def extract_location(text: str) -> str:
    candidates = []

    # Try each pattern in order
    for pat in LOCATION_PATTERNS:
        for m in pat.finditer(text):
            loc = m.group(1).strip().rstrip(".,")
            if loc:
                candidates.append(loc)

    # Prefer a candidate that contains a known city name
    for loc in candidates:
        if any(city in loc.lower() for city in KNOWN_CITIES):
            return loc

    # Fallback: return the first candidate found
    return candidates[0] if candidates else "unknown"

# ======================================================================
# 4. ACCUSED DESCRIPTION EXTRACTOR
#    Finds number of people, vehicle, clothing/helmet descriptions.
# ======================================================================
ACCUSED_PATTERNS = [
    # "Two men on a black motorcycle"
    re.compile(
        r'((?:two|three|four|one|a group of \d+|several)\s+'
        r'(?:men|women|youths|persons|accused|suspects|individuals)'
        r'(?:[^.;]{0,80})?)',
        re.IGNORECASE
    ),
    # "the pillion rider, wearing a red helmet"
    re.compile(
        r'((?:pillion rider|rider|accused|suspect)[^.;]{0,80}'
        r'(?:wearing|riding|on|in)[^.;]{0,60})',
        re.IGNORECASE
    ),
    # Generic vehicle mention near perpetrators
    re.compile(
        r'((?:on a|on the)\s+(?:black|white|red|blue|dark|light|grey|silver)?'
        r'\s*(?:motorcycle|bike|scooter|car|auto)[^.;]{0,40})',
        re.IGNORECASE
    ),
]

def extract_accused(text: str) -> str:
    parts = []
    for pat in ACCUSED_PATTERNS:
        m = pat.search(text)
        if m:
            part = m.group(1).strip().rstrip(",;.")
            # Avoid duplicates (skip if very similar to existing part)
            if not any(part[:30].lower() in existing.lower() for existing in parts):
                parts.append(part)
    return "; ".join(parts) if parts else "unknown"

# ======================================================================
# 5. MODUS OPERANDI (MO) EXTRACTOR
#    Looks for the action sequence: approach → act → escape.
#    Builds a one-sentence summary from found clauses.
# ======================================================================
MO_APPROACH = re.compile(
    r'(came from behind|approached from behind|approached the victim|'
    r'contacted via|sent a|received a|called on)',
    re.IGNORECASE
)
MO_ACTION = re.compile(
    r'(snatched|pulled off|stole|demanded|threatened|paid|blocked|'
    r'transferred|asked to pay|broke into|abducted|attacked|stabbed)',
    re.IGNORECASE
)
MO_ESCAPE = re.compile(
    r'(fled|sped away|escaped|ran away|disconnected|blocked his number|'
    r'website stopped working)',
    re.IGNORECASE
)

# Sentence splitter
SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')

def extract_mo(text: str) -> str:
    """
    Finds the sentence(s) that best describe the method:
    the one containing the most MO signals (approach + action + escape).
    """
    sentences = SENT_SPLIT.split(text)
    best_sentence = ""
    best_score = -1

    for sent in sentences:
        score = 0
        if MO_APPROACH.search(sent): score += 2
        if MO_ACTION.search(sent):   score += 3
        if MO_ESCAPE.search(sent):   score += 2
        if score > best_score:
            best_score = score
            best_sentence = sent

    if best_score <= 0:
        return "unknown"

    # Clean up the sentence: strip leading "the", trailing refs, etc.
    mo = best_sentence.strip()
    # Remove "Complainant suffered..." suffix if it crept in
    mo = re.sub(r'\.\s*Complainant suffered.*', '.', mo)
    return mo

# ======================================================================
# 6. VICTIM PROFILE EXTRACTOR
#    Returns a structured dict with name, age, gender, occupation, contact.
# ======================================================================
GENDER_MAP = {
    "ms.": "Female", "mrs.": "Female", "mr.": "Male",
    " she ": "Female", " her ": "Female", " his ": "Male", " he ": "Male",
    "woman": "Female", "women": "Female", "lady": "Female",
    "man": "Male", "men": "Male",
}
AGE_PATTERN = re.compile(r'age[d]?\s*(\d{1,3})|(\d{1,3})\s*years?\s*old', re.IGNORECASE)
OCCUPATION_PATTERN = re.compile(
    r'\b(job seeker|student|teacher|doctor|engineer|shopkeeper|'
    r'businessman|housewife|farmer|driver|worker|officer|retired|'
    r'labourer|vendor|trader|nurse|police)\b',
    re.IGNORECASE
)
# Name: looks for "complainant Ms. X" / "complainant Mr. X" / "complainant Mrs. X"
NAME_PATTERN = re.compile(
    r'complainant\s+(?:Ms\.|Mrs\.|Mr\.)?\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)',
    re.IGNORECASE
)
# 10-digit phone number
CONTACT_PATTERN = re.compile(r'\b([6-9]\d{9})\b')

def extract_victim(text: str) -> dict:
    text_lower = text.lower()

    # Name
    name_match = NAME_PATTERN.search(text)
    name = name_match.group(1).strip() if name_match else "unknown"

    # Gender
    gender = "unknown"
    for token, g in GENDER_MAP.items():
        if token in text_lower:
            gender = g
            break

    # Age (return as int if found)
    age_match = AGE_PATTERN.search(text)
    if age_match:
        age = int(age_match.group(1) or age_match.group(2))
    else:
        age = "unknown"

    # Occupation
    occ_match = OCCUPATION_PATTERN.search(text)
    occupation = occ_match.group(1).title() if occ_match else "unknown"

    # Contact number
    contact_match = CONTACT_PATTERN.search(text)
    contact = contact_match.group(1) if contact_match else "unknown"

    return {
        "name":       name,
        "age":        age,
        "gender":     gender,
        "occupation": occupation,
        "contact":    contact,
    }

# ======================================================================
# 7. MAIN PIPELINE — analyse one FIR
# ======================================================================
def analyze_fir(fir: dict) -> dict:
    text = fir["text"]
    return {
        "id":                  fir["id"],
        "crime_type":          classify_crime(text),
        "date":                extract_date(text),
        "location":            extract_location(text),
        "suspect_description": extract_accused(text),
        "modus_operandi":      extract_mo(text),
        "victim_profile":      extract_victim(text),
    }


def analyze_batch(firs: list) -> list:
    results = []
    for i, fir in enumerate(firs, start=1):
        print(f"[{i}/{len(firs)}] Analysing {fir['id']} ...")
        record = analyze_fir(fir)
        results.append(record)
        print(f"   crime_type  : {record['crime_type']}")
        print(f"   date        : {record['date']}")
        print(f"   location    : {record['location']}")
        print(f"   modus_operandi : {record['modus_operandi'][:80]}...")
    return results

# ======================================================================
# 8. RUN
# ======================================================================
if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        firs = json.load(f)

    print(f"Loaded {len(firs)} FIR(s) from {INPUT_FILE}\n")
    results = analyze_batch(firs)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nDone! {len(results)}/{len(firs)} FIR(s) saved to {OUTPUT_FILE}")
    print("\n--- FULL OUTPUT ---")
    print(json.dumps(results, indent=2, ensure_ascii=False))
