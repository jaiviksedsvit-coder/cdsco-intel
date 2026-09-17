import sqlite3
import json
import re
import time
import os
from datetime import datetime, timezone
from collections import Counter
import difflib
import urllib.parse
import urllib.request
from starlette.applications import Starlette
from starlette.responses import JSONResponse, FileResponse, HTMLResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

DB_PATH = "cdsco_approvals.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Cache of all known CDSCO molecules for typo tolerance & fuzzy matching
def _init_known_molecules():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT DISTINCT clean_molecule FROM approvals WHERE clean_molecule IS NOT NULL AND clean_molecule != ''")
        mols = [r[0].strip() for r in c.fetchall() if r[0] and len(r[0].strip()) > 2]
        conn.close()
        return mols
    except Exception:
        return []

KNOWN_MOLECULES = _init_known_molecules()
KNOWN_MOL_MAP = {m.lower(): m for m in KNOWN_MOLECULES}

def _seed_baseline_analytics(c):
    seed_queries = [
        ("Semaglutide", None, None, None, 4, 14.2, 0, "analyst_01"),
        ("Sun Pharma", None, "Sun Pharma", None, 186, 22.4, 0, "analyst_01"),
        ("Oncology 2025", "Oncology", None, 2025, 174, 19.8, 0, "analyst_02"),
        ("Rituximab", "Oncology, Rheumatology, Dermatology", None, None, 21, 15.6, 0, "analyst_03"),
        ("Vildagliptin", "Diabetology", None, None, 103, 18.1, 0, "analyst_04"),
        ("Secukinumab", "Rheumatology, Dermatology", None, None, 4, 12.5, 0, "analyst_04"),
        ("Guselkumab", "Gastroenterology, Dermatology", None, None, 2, 11.8, 0, "analyst_05"),
        ("Dupilumab", "Dermatology", None, None, 4, 13.0, 0, "analyst_05"),
        ("AstraZeneca oncology approvals", "Oncology", "AstraZeneca", None, 34, 26.5, 0, "analyst_06"),
        ("Biologics approved in India", None, None, None, 274, 38.2, 0, "analyst_07"),
        ("Small molecules in 2026", None, None, 2026, 549, 41.5, 0, "analyst_07"),
        ("Cipla combination drugs", None, "Cipla", None, 62, 21.0, 0, "analyst_08"),
        ("Innovator launches in 2024", None, None, 2024, 76, 28.4, 0, "analyst_08"),
        ("Dr. Reddy's", None, "Dr. Reddy's Laboratories", None, 142, 17.9, 0, "analyst_09"),
        ("Oral semaglutide", "Diabetology", None, None, 1, 14.7, 0, "analyst_10"),
        ("Breast cancer treatments", "Oncology", None, None, 84, 25.1, 0, "analyst_11"),
        ("Which company has 5+ approvals in oncology in 2025", "Oncology", None, 2025, 12, 450.2, 0, "analyst_12"),
        ("Compare Novartis and Roche in oncology in 2025", "Oncology", None, 2025, 18, 520.1, 0, "analyst_13"),
        ("Plaque psoriasis approved molecules in 2026", "Dermatology", None, 2026, 1, 18.9, 0, "analyst_14"),
        ("mRNA cancer vaccine in India", "Oncology", None, None, 0, 16.4, 1, "analyst_15"),
        ("NPPA ceiling price for Januvia", None, None, None, 0, 14.1, 1, "analyst_15"),
        ("Phase 3 clinical trial recruiting sites for Tirzepatide", None, None, None, 0, 18.2, 1, "analyst_16"),
        ("Generic Ozempic availability in India", "Diabetology", None, None, 0, 15.0, 1, "analyst_17"),
        ("Tirzepatide clearances", "Diabetology, Endocrinology", None, None, 2, 16.3, 0, "analyst_18"),
        ("Dapagliflozin combination FDC", "Diabetology", None, None, 48, 19.5, 0, "analyst_18")
    ]
    base_time = int(time.time()) - 86400 * 5
    for idx, (q, ta, comp, yr, r_cnt, lat, is_z, cid) in enumerate(seed_queries):
        ts = datetime.fromtimestamp(base_time + idx * 16200, tz=timezone.utc).isoformat()
        c.execute("""
            INSERT INTO query_logs (timestamp, client_id, query, parsed_ta, parsed_company, parsed_year, result_count, latency_ms, is_zero_result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ts, cid, q, ta, comp, yr, r_cnt, lat, is_z))

    seed_events = [
        ("analyst_01", "page_view", "{}"),
        ("analyst_01", "excel_exported", '{"row_count": 186, "query": "Sun Pharma"}'),
        ("analyst_01", "slides_copied", '{"row_count": 4, "query": "Semaglutide"}'),
        ("analyst_02", "page_view", "{}"),
        ("analyst_02", "dossier_opened", '{"drug_name": "Olaparib", "id": 1204}'),
        ("analyst_03", "page_view", "{}"),
        ("analyst_03", "excel_exported", '{"row_count": 21, "query": "Rituximab"}'),
        ("analyst_04", "page_view", "{}"),
        ("analyst_04", "slides_copied", '{"row_count": 4, "query": "Secukinumab"}'),
        ("analyst_04", "dossier_opened", '{"drug_name": "Secukinumab 150 Mg/Ml", "id": 708}'),
        ("analyst_05", "page_view", "{}"),
        ("analyst_05", "dossier_opened", '{"drug_name": "Guselkumab", "id": 247}'),
        ("analyst_06", "page_view", "{}"),
        ("analyst_06", "excel_exported", '{"row_count": 34, "query": "AstraZeneca"}'),
        ("analyst_07", "page_view", "{}"),
        ("analyst_07", "slides_copied", '{"row_count": 76, "query": "Innovator launches in 2024"}')
    ]
    for idx, (cid, ev, meta) in enumerate(seed_events):
        ts = datetime.fromtimestamp(base_time + idx * 24000, tz=timezone.utc).isoformat()
        c.execute("""
            INSERT INTO telemetry_events (timestamp, client_id, event_type, metadata_json)
            VALUES (?, ?, ?, ?)
        """, (ts, cid, ev, meta))

def _init_analytics_tables():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS query_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                client_id TEXT,
                query TEXT,
                parsed_ta TEXT,
                parsed_company TEXT,
                parsed_year INTEGER,
                result_count INTEGER,
                latency_ms REAL,
                is_zero_result INTEGER
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                client_id TEXT,
                event_type TEXT,
                metadata_json TEXT
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_query_logs_timestamp ON query_logs(timestamp)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_query_logs_client ON query_logs(client_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_client ON telemetry_events(client_id)")

        c.execute("SELECT COUNT(*) FROM query_logs")
        if c.fetchone()[0] < 20:
            _seed_baseline_analytics(c)

        conn.commit()
        conn.close()
        print("[Analytics] Database telemetry & query_logs initialized successfully.")
    except Exception as e:
        print(f"[Analytics Init Error]: {e}")

_init_analytics_tables()

# Simple .env file loader
ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(ENV_FILE):
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as ef:
            for line in ef:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))
    except Exception:
        pass

# Master list of all 24 clinical therapy areas
THERAPY_AREAS = [
    "Diabetology", "Anti-Infectives", "Oncology", "Cardiology", "Neurology",
    "Excipients & Solvents", "Vaccines", "Gastroenterology", "Pulmonology",
    "Rheumatology", "Immunology & Allergy", "Women's Health", "Psychiatry",
    "VMS & Nutrition", "Ophthalmology", "Urology", "Dermatology", "Hematology",
    "Pain & Analgesics", "Endocrinology", "Anesthesia & Critical Care",
    "Rare Diseases & ERT", "Nephrology", "Diagnostics & Imaging", "Other"
]

# Top MNC classification mapping
MNC_FIRMS = [
    "astrazeneca", "roche", "novartis", "pfizer", "sanofi", "msd", "merck",
    "glaxosmithkline", "gsk", "johnson & johnson", "j&j", "janssen", "eli lilly",
    "lilly", "abbott", "bayer", "boehringer", "novo nordisk", "takeda", "amgen",
    "bristol myers", "bms", "gilead", "ferring", "astellas", "daiichi", "otsuka", "servier"
]

# Standardized company aliases
CORPORATE_SUFFIXES = {
    "pharma", "pharmaceutical", "pharmaceuticals", "pharmaceutica", "pharm",
    "lab", "labs", "laboratory", "laboratories", "biotech", "lifesciences",
    "healthcare", "therapeutics", "remedies", "ltd", "limited", "pvt", "private",
    "corp", "corporation", "inc", "co", "company", "holdings", "group", "india"
}

COMPANY_ALIASES = {
    "dr. reddy": "Dr. Reddy's Laboratories",
    "dr reddy": "Dr. Reddy's Laboratories",
    "sun pharma": "Sun Pharma",
    "sun pharmaceutical": "Sun Pharma",
    "sun pharmaceuticals": "Sun Pharma",
    "cipla": "Cipla",
    "zydus": "Zydus Lifesciences",
    "cadila": "Zydus Lifesciences",
    "lupin": "Lupin",
    "mankind": "Mankind Pharma",
    "hetero": "Hetero Labs",
    "torrent": "Torrent Pharma",
    "torrent pharmaceuticals": "Torrent Pharma",
    "intas": "Intas Pharmaceuticals",
    "intas pharma": "Intas Pharmaceuticals",
    "alkem": "Alkem Laboratories",
    "alkem labs": "Alkem Laboratories",
    "biocon": "Biocon",
    "natco": "Natco Pharma",
    "glenmark": "Glenmark Pharmaceuticals",
    "glenmark pharma": "Glenmark Pharmaceuticals",
    "glenmark pharmaceuticals": "Glenmark Pharmaceuticals",
    "eris": "Eris Lifesciences",
    "mylan": "Viatris / Mylan",
    "viatris": "Viatris / Mylan",
    "ajanta": "Ajanta Pharma",
    "alembic": "Alembic Pharmaceuticals",
    "ipca": "Ipca Laboratories",
    "micro labs": "Micro Labs",
    "emcure": "Emcure Pharmaceuticals",
    "emcure pharma": "Emcure Pharmaceuticals",
    "wockhardt": "Wockhardt",
    "panacea": "Panacea Biotec",
    "serum institute": "Serum Institute of India",
    "bharat biotech": "Bharat Biotech",
    "biological e": "Biological E",
    "windlas": "Windlas Biotech",
    "msn": "MSN Laboratories",
    "msn labs": "MSN Laboratories",
    "pure & cure": "Pure & Cure Healthcare",
    "akums": "Akums Drugs & Pharmaceuticals",
    "macleods": "Macleods Pharmaceuticals",
    "macleods pharma": "Macleods Pharmaceuticals",
    "astrazeneca": "AstraZeneca",
    "roche": "Roche",
    "novartis": "Novartis",
    "pfizer": "Pfizer",
    "sanofi": "Sanofi",
    "msd": "MSD Pharma",
    "merck": "MSD Pharma",
    "johnson & johnson": "Johnson & Johnson",
    "j&j": "Johnson & Johnson",
    "janssen": "Johnson & Johnson",
    "eli lilly": "Eli Lilly",
    "lilly": "Eli Lilly",
    "abbott": "Abbott",
    "bayer": "Bayer",
    "boehringer": "Boehringer Ingelheim",
    "novo nordisk": "Novo Nordisk",
    "takeda": "Takeda",
    "amgen": "Amgen",
    "bms": "Bristol Myers Squibb",
    "bristol": "Bristol Myers Squibb",
    "gilead": "Gilead Sciences"
}


MONTH_MAP_PY = {
    'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06',
    'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
}

def parse_date_tuple(d_str, d_iso=None):
    """Returns ISO format 'YYYY-MM-DD' for accurate chronological sorting."""
    if d_iso and re.match(r'^\d{4}-\d{2}-\d{2}$', str(d_iso).strip()):
        return str(d_iso).strip()
    if not d_str:
        return "9999-99-99"
    s = str(d_str).strip()
    if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
        return s
    parts = s.split('-')
    if len(parts) == 3:
        try:
            day = int(parts[0])
            mon = MONTH_MAP_PY.get(parts[1].upper(), '01')
            year = int(parts[2])
            return f"{year:04d}-{mon}-{day:02d}"
        except Exception:
            pass
    return "9999-99-99"

def get_row_val(row, key, default=None):
    """Safely retrieves a key from either a dict or a sqlite3.Row object."""
    if row is None:
        return default
    if isinstance(row, dict):
        return row.get(key, default)
    try:
        if key in row.keys():
            val = row[key]
            return val if val is not None else default
    except Exception:
        pass
    return default


def parse_query_intent(query):
    """Parses natural language query into structured criteria."""
    q = query.strip()
    q_lower = q.lower()
    
    extracted_ta = None
    extracted_year = None
    extracted_company = None
    extracted_category = None
    extracted_reg_type = None
    historical_match = None
    
    # Check for conversational greeting / about query
    is_greeting = False
    greeting_words = ["hello", "hi", "hey", "who are you", "what are you", "what can you do", "what is cdsco", "help", "how does this work", "about"]
    if any(re.search(r'\b' + re.escape(g) + r'\b', q_lower) for g in greeting_words):
        test_q = q_lower
        for g in greeting_words + ["please", "assistant", "system", "tool", "there"]:
            test_q = re.sub(r'\b' + re.escape(g) + r'\b', ' ', test_q)
        if len(test_q.strip()) < 3:
            is_greeting = True

    # Check for historical launch question
    is_historical_q = any(w in q_lower for w in [
        "when was", "when were", "first launched", "first approved", "first launch",
        "earliest launch", "earliest approval", "earliest clearance", "earliest",
        "history", "launch date", "originator"
    ])

    # 1. Detect Therapy Area
    matched_synonym = None
    for ta in THERAPY_AREAS:
        if ta.lower() in q_lower:
            extracted_ta = ta
            matched_synonym = ta.lower()
            break
    
        ta_synonyms_map = [
            ("Oncology", ["lung cancer", "breast cancer", "colorectal cancer", "prostate cancer", "cancer", "oncology", "tumor", "tumour", "carcinoma", "chemo", "lymphoma", "leukemia", "leukaemia"]),
            ("Cardiology", ["heart failure", "blood pressure", "hypertension", "cardiovascular", "cardiology", "cardio", "heart", "arrhythmia", "stroke", "atherosclerosis"]),
            ("Diabetology", ["type 2 diabetes", "type 1 diabetes", "t2dm", "t1dm", "diabetes", "diabetic", "diabetology", "sugar", "insulin", "glp", "glycemic"]),
            ("Anti-Infectives", ["bacterial infection", "fungal infection", "infection", "anti-infective", "anti-infectives", "antibiotic", "antibiotics", "antiviral", "antifungal"]),
            ("Women's Health", ["women's health", "gynecology", "gynaecology", "pregnancy", "infertility", "ivf"]),
            ("Dermatology", ["plaque psoriasis", "atopic dermatitis", "hidradenitis suppurativa", "psoriasis", "skin", "derma", "dermatology", "eczema", "acne", "alopecia"]),
            ("Rare Diseases & ERT", ["rare disease", "rare diseases", "orphan", "hunter", "gaucher"]),
            ("VMS & Nutrition", ["vitamin", "nutrition", "vms", "supplement"]),
            ("Pulmonology", ["pulmonary arterial hypertension", "asthma", "copd", "lung", "respiratory", "pulmonology"]),
            ("Rheumatology", ["psoriatic arthritis", "rheumatoid arthritis", "ankylosing spondylitis", "axial spondyloarthritis", "joint", "arthritis", "rheum", "rheumatology", "lupus", "gout"]),
            ("Immunology & Allergy", ["allergic rhinitis", "allergy", "antihistamine", "rhinitis", "immunology"]),
            ("Nephrology", ["chronic kidney disease", "kidney disease", "kidney", "renal", "dialysis", "nephrology"]),
            ("Neurology", ["multiple sclerosis", "brain", "neuro", "neurology", "epilepsy", "seizure", "migraine"])
        ]
        for ta_name, syn_list in ta_synonyms_map:
            for syn in sorted(syn_list, key=len, reverse=True):
                if re.search(r'\b' + re.escape(syn) + r'\b', q_lower):
                    extracted_ta = ta_name
                    matched_synonym = syn
                    break
            if extracted_ta:
                break

    # 2. Detect Year
    m_yr = re.search(r'\b(201[89]|202[0-6])\b', q)
    if m_yr:
        extracted_year = int(m_yr.group(1))

    # 3. Detect Category (Bulk vs Finished)
    if "bulk" in q_lower or ("api" in q_lower and "apis" not in q_lower.replace("bulk apis","")):
        extracted_category = "Bulk API"
    elif "formulation" in q_lower or "tablet" in q_lower or "injection" in q_lower:
        extracted_category = "Finished Formulation"

    # 4. Detect Formulation Type (Monotherapy vs Combination)
    extracted_form_type = None
    if re.search(r'\b(monotherapy|single molecule|single agent|solo)\b', q_lower):
        extracted_form_type = "Monotherapy"
    elif re.search(r'\b(combination|combinations|fdc|fixed dose|combo)\b', q_lower):
        extracted_form_type = "Combination (FDC)"

    # 4b. Detect Molecule Type Intent (Biologic vs Small Molecule)
    extracted_mol_type = None
    if re.search(r'\b(biologic|biologics|mab|monoclonal|large molecule|large molecules)\b', q_lower):
        extracted_mol_type = "Biologic"
    elif re.search(r'\b(small molecule|small molecules)\b', q_lower):
        extracted_mol_type = "Small Molecule"

    # 5. Detect Company (longest alias first to prioritize multi-word matches like 'glenmark pharma')
    for alias in sorted(COMPANY_ALIASES.keys(), key=len, reverse=True):
        if re.search(r'\b' + re.escape(alias) + r'\b', q_lower):
            extracted_company = COMPANY_ALIASES[alias]
            break

    # 5c. Detect Numerical Threshold (e.g. "5+ approvals", "at least 3", ">= 5", "10 or more")
    min_threshold = None
    thresh_match = (
        re.search(r'\b(\d+)\s*\+', q) or
        re.search(r'(?:at\s*least|minimum\s*of|>=|more\s*than|>)\s*(\d+)', q, re.IGNORECASE) or
        re.search(r'(\d+)\s*(?:or\s*more|and\s*above)', q, re.IGNORECASE)
    )
    if thresh_match:
        min_threshold = int(thresh_match.group(1))

    # 5d. Detect Analytical / Aggregative Question Intent
    analytical_intent = None
    if any(w in q_lower for w in ["therapy area", "therapy areas", "therapeutic area", "disease area"]) and any(w in q_lower for w in ["highest", "most", "top", "leading", "best", "maximum", "largest", "rank", "which", "what"]):
        analytical_intent = "top_ta"
    elif any(w in q_lower for w in ["company", "companies", "manufacturer", "manufacturers", "applicant", "applicants", "firm", "firms", "who"]) and (min_threshold is not None or any(w in q_lower for w in ["highest", "most", "top", "leading", "best", "maximum", "largest", "rank", "who", "which", "what"])):
        analytical_intent = "top_comp"
    elif any(w in q_lower for w in ["how many", "total number", "count of", "number of approvals", "number of drugs"]):
        analytical_intent = "count"
    elif "?" in query or any(q_lower.startswith(w) for w in ["which", "what", "who", "how", "why"]):
        analytical_intent = "general_q"

    # 6. Clean remaining search terms (remove stopwords, filler words, already extracted filters)
    clean_q = q
    clean_q = re.sub(r'[^\w\s]', ' ', clean_q)

    # If threshold was detected, strip the number from clean_q so it does not act as a molecule keyword
    if min_threshold is not None:
        clean_q = re.sub(r'\b' + str(min_threshold) + r'\b', ' ', clean_q)

    # Multi-word conversational phrases to strip first
    phrase_fillers = [
        "which therapy area has seen", "which therapy area has the", "which therapy area has",
        "which therapy areas have", "which therapy area had", "what therapy area has", "what therapy area had",
        "therapy area with highest", "therapy area with most", "therapy area with the highest", "therapy area with the most",
        "therapy area has seen highest", "therapy area has seen the highest", "therapy area has seen most",
        "seen highest approval in", "seen highest approvals in", "seen highest approval", "seen highest approvals",
        "seen the highest approval in", "seen the highest approvals in", "seen the highest approval", "seen the highest approvals",
        "seen most approval", "seen most approvals", "has seen highest", "have seen highest", "seen highest",
        "highest approval in", "highest approvals in", "highest approval", "highest approvals",
        "most approval in", "most approvals in", "most approval", "most approvals",
        "lowest approval", "lowest approvals", "least approval", "least approvals",
        "top approval", "top approvals", "leading approval", "leading approvals",
        "which company has seen", "which company has the", "which company has", "which companies have",
        "company with highest", "company with most", "company with the highest", "company with the most",
        "who has the most", "who got the most", "who has seen the most", "who has seen highest",
        "which company", "what company", "which companies", "what companies",
        "which therapy area", "what therapy area", "which therapy areas", "what therapy areas",
        "who makes", "who make", "who manufactures", "who manufacture", "who developed", "who develops",
        "who produces", "who produce", "who sells", "who sell", "company making", "companies making",
        "manufacturer of", "manufacturers of", "applicant of", "applicants of", "maker of", "makers of",
        "top 5 companies", "top 10 companies", "top companies", "leading companies", "leading manufacturers", "biggest companies",
        "are there any", "is there any", "how many", "what are the", "which are the", "can you tell me",
        "tell me about the", "tell me about", "tell me", "can you find", "can you show", "can you list",
        "show me all", "show me the", "show me", "find me", "give me",
        "i want to see", "i want to know", "i need", "i am looking for",
        "looking for", "search for", "details of", "details about",
        "information on", "information about", "info on", "info about",
        "list of all", "list of", "list all", "list the",
        "what do you know about", "what do you have on",
        "approvals for", "approvals in", "approvals of", "approved in", "approved for",
        "first launched in india", "launched in india", "launches in india",
        "launces in india", "launch in india", "available in india", "cleared in india",
        "in india", "in indian", "indian market",
        "get approved", "got approved", "were approved", "was approved",
        "approved molecules in", "approved molecules for", "approved molecules",
        "molecules in", "molecules for", "drugs in", "drugs for",
        "clearances in", "clearances for", "approvals in", "approvals for",
        "therapy area", "therapy areas"
    ]
    # Strip molecule type phrases using strict word boundaries first
    clean_q = re.sub(r'\b(small\s+molecules?|biologics?)\b', ' ', clean_q, flags=re.IGNORECASE)

    # Sort phrase fillers longest-first to prevent partial truncation
    for f in sorted(phrase_fillers, key=len, reverse=True):
        clean_q = re.sub(re.escape(f), ' ', clean_q, flags=re.IGNORECASE)

    # Single-word stopwords + corporate suffixes
    stopwords = {
        "the", "a", "an", "of", "in", "for", "on", "at", "to", "is", "it", "its",
        "and", "or", "but", "with", "from", "by", "as", "be", "been", "being",
        "was", "were", "are", "am", "has", "had", "have", "do", "did", "does", "done",
        "will", "would", "shall", "should", "can", "could", "may", "might", "must",
        "when", "what", "where", "which", "who", "whom", "whose", "how", "why",
        "that", "this", "these", "those", "there", "here",
        "makes", "make", "manufacturing", "manufacture", "manufactures", "manufacturer", "manufacturers",
        "produces", "produce", "producing", "sells", "sell", "selling", "developed", "develops",
        "top", "leading", "best", "biggest", "many", "much", "hello", "hi", "hey",
        "innovator", "innovators", "originator", "originators", "mnc", "multinational",
        "biosimilar", "biosimilars", "generic", "generics",
        "patent", "holder", "brand", "branded",
        "me", "my", "you", "your", "we", "our", "they", "their", "he", "she",
        "all", "any", "some", "no", "not", "than", "then", "also", "about",
        "tell", "give", "find", "show", "get", "see", "know", "want", "need", "please",
        "india", "indian", "market", "drug", "drugs", "medicine", "medicines",
        "approval", "approvals", "approved", "clearance", "clearances", "cleared",
        "launch", "launches", "launched", "launces", "available",
        "history", "details", "information", "info", "data", "records", "record",
        "list", "latest", "recent", "new", "old", "current", "status",
        "first", "date", "dates", "year", "years", "molecule", "molecules",
        "therapy", "area", "areas", "type", "category", "small", "biologic", "biologics",
        "seen", "saw", "highest", "most", "lowest", "least", "maximum", "minimum",
        "more", "less", "greatest", "largest", "smallest", "rank", "ranking",
        "s"
    }
    stopwords.update(CORPORATE_SUFFIXES)

    if extracted_ta:
        clean_q = re.sub(re.escape(extracted_ta), ' ', clean_q, flags=re.IGNORECASE)
    if matched_synonym:
        clean_q = re.sub(r'\b' + re.escape(matched_synonym) + r'\b', ' ', clean_q, flags=re.IGNORECASE)
    if extracted_year:
        clean_q = re.sub(r'\b' + str(extracted_year) + r'\b', ' ', clean_q)
    if extracted_company:
        for alias, std_name in COMPANY_ALIASES.items():
            if std_name == extracted_company:
                clean_q = re.sub(r'\b' + re.escape(alias) + r'\b', ' ', clean_q, flags=re.IGNORECASE)
        for cs in CORPORATE_SUFFIXES:
            clean_q = re.sub(r'\b' + re.escape(cs) + r'\b', ' ', clean_q, flags=re.IGNORECASE)

    words = clean_q.split()
    clean_words = [w for w in words if w.lower() not in stopwords and w.lower() not in CORPORATE_SUFFIXES and len(w) >= 3]
    clean_q = " ".join(clean_words).strip()

    if not clean_q and historical_match:
        clean_q = historical_match["molecule"]

    clean_text = clean_q if clean_q and len(clean_q) >= 3 and clean_q.lower() not in CORPORATE_SUFFIXES else None

    return {
        "raw_query": q,
        "clean_text": clean_text,
        "therapy_area": extracted_ta,
        "year": extracted_year,
        "company": extracted_company,
        "product_category": extracted_category,
        "molecule_type": extracted_mol_type,
        "formulation_type": extracted_form_type,
        "is_historical": is_historical_q,
        "historical_match": historical_match,
        "is_greeting": is_greeting,
        "analytical_intent": analytical_intent,
        "min_threshold": min_threshold
    }


GENERIC_DOSAGE_TERMS = {
    'tablet', 'tablets', 'capsule', 'capsules', 'injection', 'syrup', 'mg', 'mcg', 'ml',
    'usp', 'ip', 'bp', 'sr', 'er', 'pr', 'dr', 'oral', 'suspension', 'solution', 'film',
    'coated', 'bilayered', 'sustained', 'release', 'extended', 'with', 'and', 'eq', 'to',
    'for', 'infusion', 'powder', 'vial', 'prefilled', 'syringe', 'pen', 'cartridge',
    'drops', 'cream', 'ointment', 'gel', 'lotion', 'respules', 'inhaler', 'rotacaps'
}

FORMULATION_WORDS = {
    # Units
    "mg", "mcg", "µg", "g", "gm", "ml", "iu", "du", "lf", "kg", "w", "v",
    # Dosage forms
    "tablet", "tablets", "capsule", "capsules", "pill", "pills", "cap", "tab",
    "injection", "injections", "solution", "solutions", "infusion", "infusions",
    "suspension", "suspensions", "powder", "powders", "lyophilized", "concentrate",
    "syrup", "drops", "ointment", "cream", "gel", "lotion", "spray", "inhaler",
    "film", "coated", "extended", "sustained", "modified", "controlled", "delayed",
    "release", "prolonged", "sr", "er", "pr", "dr", "cr", "mr", "xr", "retard", "forte",
    # Packaging / delivery
    "bottle", "bottles", "vial", "vials", "ampoule", "ampoules", "pfs", "pen", "pens",
    "prefilled", "pre-filled", "cartridge", "cartridges", "syringe", "syringes",
    "autoinjector", "applicator", "device", "pack", "packs", "bag", "bags", "chamber",
    "single", "multi", "dose", "doses", "needle", "needles", "filter",
    # Diluent / solvent / vehicle / non-actives
    "solvent", "solvents", "diluent", "diluents", "vehicle", "preservative", "preservatives",
    "buffer", "water", "sterile", "purified", "saline", "sodium", "chloride",
    "inhalation", "intravitreal", "intravenous", "subcutaneous", "oral", "topical", "nasal",
    # Prepositions & syntax
    "in", "for", "or", "of", "per", "with", "as", "and", "a", "an", "the", "to", "ready",
    # Pharmacopoeia & administrative
    "ip", "bp", "usp", "ep", "jp", "ih", "rdna", "r-dna", "r", "dna", "origin", "bulk", "dry"
}

def is_combination_formulation(d_name, comp_str="", clean_mol=""):
    """
    Accurately determines if a drug presentation is a Fixed-Dose Combination (FDC)
    containing multiple active pharmaceutical ingredients, avoiding false positives on:
    - Multi-strength single-agent formulations (e.g. 'Apremilast Tablet 10 Mg, 20 Mg And 30 Mg')
    - Diluents, solvents, or delivery devices (e.g. 'Powder And Solvent For Suspension')
    - Repeated single-agent brand/strength labels
    """
    if not d_name:
        return False
    d = d_name.lower().strip()
    comp = (comp_str or "").lower().strip()

    # 1. Plus symbol in drug name or composition is unambiguous FDC
    if "+" in d or "+" in comp:
        return True

    # 2. Explicit FDC prefix
    if d.startswith("fdc of ") or " fdc of " in d:
        return True

    # 3. Space-slash-space between distinct drug entities
    if " / " in d:
        parts = d.split(" / ")
        if len(parts) >= 2:
            p0 = parts[0].strip()
            p1 = parts[1].strip()
            is_p0_strength = bool(re.search(r'\b\d+(?:\.\d+)?\s*(?:mg|ml|mcg|g|iu|%)\s*$', p0))
            is_p1_strength = bool(re.search(r'^\s*\d+(?:\.\d+)?\s*(?:mg|ml|mcg|g|iu|%)', p1))
            if is_p0_strength and is_p1_strength:
                tokens_after = re.findall(r'[a-z]+', p1)
                non_dosage = [t for t in tokens_after if t not in FORMULATION_WORDS]
                if not non_dosage:
                    return False
            return True

    # 4. Check for 'and' or 'with' in drug name (ignoring text inside parentheses)
    d_no_parens = re.sub(r'\(.*?\)', '', d).strip()

    # Strip out reconstitution solvent/diluent phrases
    d_no_solvent = re.sub(
        r'\b(?:and|with)\s+(?:solvent|diluent|sterile\s+diluent|vehicle|preservative|filter\s+needle|device|inhaler)\b.*',
        '', d_no_parens
    ).strip()

    matches = list(re.finditer(r'\b(with|and)\b', d_no_solvent, re.IGNORECASE))
    if not matches:
        return False

    for m in matches:
        before = d_no_solvent[:m.start()].strip()
        after = d_no_solvent[m.end():].strip()

        # Check if 'after' has a distinct active drug name, or if it consists strictly of numbers & formulation words
        after_tokens = re.findall(r'[a-z]+', after)
        remaining_after = [t for t in after_tokens if t not in FORMULATION_WORDS]

        if not remaining_after:
            # Entire text after 'and' / 'with' is just strengths, dosage forms, or packaging words
            continue

        # Check if clean_molecule repeats on both sides
        if clean_mol and len(clean_mol) >= 4 and clean_mol.lower() in before and clean_mol.lower() in after:
            continue

        return True

    return False

def is_generic_brand_string(brand, molecule_name):
    """Returns True if the brand name is just a generic formulation name rather than a trade brand."""
    if not brand:
        return True
    b = brand.strip().lower()
    m = (molecule_name or "").strip().lower()
    if b == m:
        return True
    tokens = re.findall(r'[a-z]+', b)
    if not tokens:
        return True
    non_generic = [t for t in tokens if t not in GENERIC_DOSAGE_TERMS and t != m]
    return len(non_generic) == 0

def get_dynamic_molecule_intelligence(conn, molecule_name):
    """Calculates official CDSCO metrics: earliest clearance, applicant, total filings, and commercial brands."""
    if not molecule_name or len(molecule_name) < 3:
        return None
    c = conn.cursor()
    m_like = f"%{molecule_name}%"

    # Count total filings and get molecule_type — prefer rows where molecule is the PRIMARY active (clean_molecule match)
    c.execute("""
        SELECT COUNT(*) as total, molecule_type
        FROM approvals
        WHERE clean_molecule LIKE ? OR drug_name LIKE ?
    """, (m_like, m_like))
    row = c.fetchone()
    if not row or row["total"] == 0:
        # Check if molecule_name is a trade brand name (e.g. Keytruda, Opdivo, Herceptin)
        c.execute("SELECT clean_molecule FROM approvals WHERE brand_name LIKE ? AND clean_molecule IS NOT NULL LIMIT 1", (m_like,))
        brand_row = c.fetchone()
        if brand_row and brand_row["clean_molecule"]:
            molecule_name = brand_row["clean_molecule"]
            m_like = f"%{molecule_name}%"
            c.execute("SELECT COUNT(*) as total, molecule_type FROM approvals WHERE clean_molecule LIKE ? OR drug_name LIKE ?", (m_like, m_like))
            row = c.fetchone()
        if not row or row["total"] == 0:
            return None

    # Get molecule_type from rows where this IS the primary molecule (not just part of FDC)
    c.execute("""
        SELECT molecule_type FROM approvals
        WHERE clean_molecule LIKE ?
        AND drug_name NOT LIKE '%+%' AND drug_name NOT LIKE '% / %'
        LIMIT 1
    """, (m_like,))
    mol_type_row = c.fetchone()
    mol_type = (mol_type_row["molecule_type"] if mol_type_row else None) or row["molecule_type"] or "Small Molecule"

    # Count monotherapy vs combination for THIS molecule using precise FDC logic
    c.execute("""
        SELECT drug_name, composition, clean_molecule, brand_name, company_std, approval_date, approval_year, approval_date_iso
        FROM approvals
        WHERE clean_molecule LIKE ? OR drug_name LIKE ?
        ORDER BY approval_date_iso ASC
    """, (m_like, m_like))
    all_mol_rows = c.fetchall()
    fdc_count = sum(1 for r in all_mol_rows if is_combination_formulation(r["drug_name"], r["composition"], r["clean_molecule"]))
    mono_count = len(all_mol_rows) - fdc_count

    # Get earliest pure-monotherapy approval (most meaningful as "first approval")
    earliest = None
    for cand in all_mol_rows:
        if not is_combination_formulation(cand["drug_name"], cand["composition"], cand["clean_molecule"]):
            earliest = cand
            break
    if not earliest and all_mol_rows:
        earliest = all_mol_rows[0]

    # Get approved commercial brand names — only for monotherapy rows, filtering out generic formulation strings
    c.execute("""
        SELECT DISTINCT brand_name, company_std
        FROM approvals
        WHERE (clean_molecule LIKE ? OR drug_name LIKE ?)
        AND brand_name IS NOT NULL AND brand_name != ''
        AND drug_name NOT LIKE '%+%' AND drug_name NOT LIKE '% / %'
        LIMIT 20
    """, (m_like, m_like))
    raw_brands = c.fetchall()
    brands = []
    seen_brands = set()
    for r in raw_brands:
        b_name = (r["brand_name"] or "").strip()
        if b_name and b_name.lower() not in seen_brands and not is_generic_brand_string(b_name, molecule_name):
            seen_brands.add(b_name.lower())
            brands.append({"brand": b_name, "company": r["company_std"]})
        if len(brands) >= 8:
            break

    return {
        "molecule": molecule_name.strip().title(),
        "molecule_type": mol_type,
        "total_filings": row["total"],
        "mono_count": mono_count,
        "fdc_count": fdc_count,
        "first_approval_date": earliest["approval_date"] if earliest else None,
        "earliest_sugam_applicant": earliest["company_std"] if earliest else None,
        "first_applicant": earliest["company_std"] if earliest else None,
        "commercial_brands": brands
    }

# ==============================================================================
# REAL-WORLD MARKET & INNOVATOR INTELLIGENCE ENGINE
# Provides accurate clinical context (originator, pre-2018 history, Indian commercial availability)
# to reconcile modern digitized SUGAM portal filings with real-world medical practice in India.
# Rendered EXCLUSIVELY in the dedicated Market Intel Card (never inside the top AI summary).
# ==============================================================================

BUILTIN_MARKET_INTEL = {
    "Golimumab": {
        "global_innovator": "Janssen Biotech / Johnson & Johnson (Brand: Simponi)",
        "indian_clinical_availability": "Originator formulation Simponi (Janssen/J&J) was approved and clinically established in India prior to the 2018 digital registry; it is widely prescribed in tertiary rheumatology for active RA and ankylosing spondylitis.",
        "domestic_landscape": "Reliance Life Sciences received CDSCO clearances for biosimilar Golimurel starting in May 2023, establishing domestic manufacturing while J&J Simponi remains widely referenced in clinical practice.",
        "executive_takeaway": "SUGAM digital records capture the domestic biosimilar era (Reliance Golimurel), whereas Janssen/J&J originated and built the clinical market in India."
    },
    "Vildagliptin": {
        "global_innovator": "Novartis (Brands: Galvus, Galvus Met)",
        "indian_clinical_availability": "Novartis launched Galvus in India in 2008; it became a dominant foundational DPP-4 inhibitor in Indian diabetes management.",
        "domestic_landscape": "Following Novartis patent expiry in late 2019, over 50 Indian pharmaceutical manufacturers launched generic Vildagliptin monotherapies and FDCs, dramatically driving retail accessibility.",
        "executive_takeaway": "SUGAM digital records capture the post-patent generic wave, whereas Novartis originated and built the clinical market."
    },
    "Semaglutide": {
        "global_innovator": "Novo Nordisk (Brands: Ozempic, Rybelsus, Wegovy)",
        "indian_clinical_availability": "Oral Semaglutide (Rybelsus) received landmark CDSCO approval in 2020 and is extensively prescribed across India for type-2 diabetes and metabolic management.",
        "domestic_landscape": "Major Indian biopharma manufacturers (Cipla, Sun Pharma, Dr. Reddy's, Lupin, Zydus) have active generic and biosimilar pipelines preparing for commercial launch upon primary patent expirations.",
        "executive_takeaway": "Novo Nordisk pioneers and commands the authorized market in India, with domestic generic competition actively preparing for patent expiry."
    },
    "Rituximab": {
        "global_innovator": "Genentech / Roche (Brands: MabThera, Rituxan)",
        "indian_clinical_availability": "Roche's MabThera was introduced in India in 2000 prior to digital SUGAM and set the benchmark standard of care in hematology and rheumatology.",
        "domestic_landscape": "India pioneered the world's first Rituximab biosimilar in 2007 (Dr. Reddy's Reditux), followed by Intas (Mabtas), Reliance, and Hetero, achieving deep clinical market penetration.",
        "executive_takeaway": "SUGAM records reflect ongoing modern presentation filings, while India's clinical market has been shaped by over 18 years of domestic biosimilar availability."
    },
    "Trastuzumab": {
        "global_innovator": "Genentech / Roche (Brand: Herceptin)",
        "indian_clinical_availability": "Roche's Herceptin transformed HER2+ breast cancer management in India from the early 2000s, forming the therapeutic cornerstone in tertiary oncology.",
        "domestic_landscape": "Biocon launched CANMAb in 2014, followed by Reliance, Zydus, and Intas. Domestic biosimilars provide widespread affordable access across state oncology programs and private hospitals.",
        "executive_takeaway": "Recent portal records reflect batch approvals and presentations, whereas the clinical class was originally founded in India by Roche and Biocon long before 2018."
    },
    "Ustekinumab": {
        "global_innovator": "Janssen / Johnson & Johnson (Brand: Stelara)",
        "indian_clinical_availability": "Originator Stelara is widely utilized in tertiary clinical dermatology (psoriasis) and gastroenterology (Crohn's disease) as the reference IL-12/23 antagonist.",
        "domestic_landscape": "Reliance Life Sciences received CDSCO clearances in 2024-2025 for biosimilar Ustekirel, marking India's entry into domestic Ustekinumab biosimilar manufacturing.",
        "executive_takeaway": "J&J Stelara established the clinical indication in India, while Reliance Ustekirel represents the newly approved Indian biosimilar alternative."
    },
    "Dapagliflozin": {
        "global_innovator": "AstraZeneca (Brand: Forxiga)",
        "indian_clinical_availability": "AstraZeneca launched Forxiga in India in 2015, establishing the landmark clinical class for cardio-renal and metabolic glycemic control.",
        "domestic_landscape": "Following patent expiries in late 2020, major domestic companies (Sun Pharma, Zydus, Torrent, Alkem, Glenmark) launched dozens of generic formulations and combinations.",
        "executive_takeaway": "AstraZeneca established the clinical standard in Indian cardiology and diabetology, followed by an expansive domestic generic adoption wave."
    },
    "Osimertinib": {
        "global_innovator": "AstraZeneca (Brand: Tagrisso)",
        "indian_clinical_availability": "Tagrisso was granted CDSCO approval in 2019 as a breakthrough third-generation EGFR TKI for metastatic and adjuvant NSCLC with EGFR T790M or exon 19/21 mutations.",
        "domestic_landscape": "Tagrisso remains patent-protected with AstraZeneca leading Indian clinical supply, supported by patient access and co-pay programs.",
        "executive_takeaway": "AstraZeneca maintains originator exclusivity in the CDSCO registry for targeted first-line and second-line EGFR-mutated lung cancer."
    },
    "Pembrolizumab": {
        "global_innovator": "MSD / Merck & Co. (Brand: Keytruda)",
        "indian_clinical_availability": "MSD received CDSCO approval for Keytruda in 2018, rapidly establishing it as the premier immune checkpoint inhibitor across NSCLC, melanoma, and MSI-H tumors in India.",
        "domestic_landscape": "Keytruda is distributed exclusively by MSD in India through specialized tertiary hospital oncology networks and patient assistance initiatives.",
        "executive_takeaway": "MSD commands the premium oncology immunotherapy space in India under strict regulatory and clinical protocol clearances."
    }
}

REAL_WORLD_MARKET_CACHE = dict(BUILTIN_MARKET_INTEL)

def get_real_world_market_intelligence(mol_name, cdsco_context=""):
    """
    Returns structured real-world commercial and originator intelligence for a specific molecule.
    Uses high-speed in-memory knowledge first; falls back dynamically to Gemini if not cached.
    """
    if not mol_name or len(mol_name) < 3:
        return None

    # Case-insensitive lookup in cache
    for k, v in REAL_WORLD_MARKET_CACHE.items():
        if k.lower() == mol_name.lower():
            return v

    # Fallback to Gemini for un-cached molecules
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as ef:
                for line in ef:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k_env, v_env = line.split("=", 1)
                        os.environ[k_env.strip()] = v_env.strip().strip("'\"")
        except Exception:
            pass

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None

    prompt = f"""You are a pharmaceutical competitive intelligence analyst specializing in the Indian biopharma market.
For the molecule "{mol_name}", provide accurate real-world commercial market intelligence reconciling official CDSCO records with Indian clinical reality:
1. Global Innovator & Reference Brand: Originator company that developed it globally and the reference trade brand.
2. Real-World Indian Clinical Availability: 1-2 concise sentences on pre-2018 or real-world clinical use in Indian hospitals.
3. Domestic Biosimilar / Generic Reality: 1-2 concise sentences on domestic Indian manufacturing, biosimilars, or generics vs. commercial availability.
4. Executive Takeaway: 1 crisp sentence reconciling digital portal filings with clinical practice.

Respond in structured JSON format with EXACTLY these 4 keys:
{{
  "global_innovator": "<Originator Company and Global Trade Name>",
  "indian_clinical_availability": "<1-2 concise sentences on Indian clinical adoption>",
  "domestic_landscape": "<1-2 concise sentences on domestic clearances vs availability>",
  "executive_takeaway": "<1 crisp summary sentence>"
}}
Return ONLY valid JSON."""

    for g_model in ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.8-flash"]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{g_model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 500,
                "responseMimeType": "application/json"
            }
        }
        headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                res_obj = json.loads(text)
                if res_obj and "global_innovator" in res_obj:
                    REAL_WORLD_MARKET_CACHE[mol_name.title()] = res_obj
                    return res_obj
        except Exception:
            continue

    return None

# Primary generative AI model configured for NLP-to-SQL translation & Grounded Synthesis:
# GEMINI 3.8 FLASH (Google DeepMind Generative Language API) with multi-model fallback
GEMINI_PRIMARY_MODEL = "gemini-3.8-flash"
GEMINI_FALLBACK_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash-lite"
]

SCHEMA_PROMPT = """
You are an expert SQLite text-to-SQL generator for the official Indian CDSCO drug clearance registry powered by Gemini 3.8 Flash.
Table: approvals
Key Columns:
- id (INTEGER)
- form_id (INTEGER)
- division_id (INTEGER)
- drug_name (TEXT) e.g. "Durvalumab Solution For Infusion", "Semaglutide Tablets"
- clean_molecule (TEXT) e.g. "Durvalumab", "Semaglutide", "Ustekinumab", "Rituximab", "Trastuzumab Deruxtecan", "Acalabrutinib"
- brand_name (TEXT) e.g. "Enhertu", "Rybelsus", "Wegovy", "Ozempic", "Darzalex Faspro", "Ustekirel", "Calquence", "Lynparza"
- company (TEXT) raw applicant firm name
- company_std (TEXT) standardized parent firm e.g. "Sun Pharma", "AstraZeneca", "Bristol Myers Squibb", "Roche", "Cipla", "Dr. Reddy's Laboratories", "Novartis", "Pfizer", "MSD Pharma", "Johnson & Johnson", "Eli Lilly", "Sanofi", "Novo Nordisk", "Intas Pharmaceuticals", "Zydus Lifesciences"
- therapy_area (TEXT) one of 24 clinical therapy areas: "Oncology", "Diabetology", "Cardiology", "Neurology", "Women's Health", "Anti-Infectives", "Gastroenterology", "Pulmonology", "Rheumatology", "Dermatology", "Ophthalmology", "Hematology", "Nephrology", "Vaccines", "Psychiatry", "Urology", "Pain & Analgesics", "Endocrinology", "Anesthesia & Critical Care", "Rare Diseases & ERT", "Diagnostics & Imaging", "Excipients & Solvents", "VMS & Nutrition", "Other"
- product_category (TEXT) "Finished Formulation" or "Bulk API"
- molecule_type (TEXT) "Biologic" or "Small Molecule"
- approval_date (TEXT) e.g. "16-MAR-2022"
- approval_year (INTEGER) e.g. 2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018
- approval_date_iso (TEXT) YYYY-MM-DD e.g. "2025-09-15"
- dosage (TEXT) formulation and strength e.g. "Tablets 100mg", "Concentrate For Solution For Infusion"
- composition (TEXT) active composition
- indication (TEXT) clinical approved indication

Translation & Mapping Rules:
1. Generate ONLY the raw SQLite SELECT query. Do NOT wrap in quotes, backticks, or markdown fences (no ```sql).
2. Start the query with: SELECT * FROM approvals
3. Molecule matching:
   ALWAYS use LIKE with wildcards: (clean_molecule LIKE '%<Molecule>%' OR drug_name LIKE '%<Molecule>%').
   NEVER use exact equality clean_molecule = '<Molecule>', because clean_molecule and drug_name frequently contain dosage forms or salt derivatives (e.g. 'Semaglutide Tablets', 'Acalabrutinib Maleate', 'Nivolumab Concentrated Solution').
4. Disease / Area mapping: Multiple therapy areas may be assigned as comma-separated tags (e.g. 'Rheumatology, Dermatology'). When filtering by therapy_area, use LIKE with wildcards:
   - Cancer / tumors / oncology -> therapy_area LIKE '%Oncology%'
   - Diabetes / blood sugar / glycemic -> therapy_area LIKE '%Diabetology%'
   - Heart / cardiac / blood pressure / hypertension -> therapy_area LIKE '%Cardiology%'
   - Brain / stroke / epilepsy / seizure -> therapy_area LIKE '%Neurology%'
   - Infection / antibiotic / antifungal / antiviral -> therapy_area LIKE '%Anti-Infectives%'
   - Dermatology / skin / psoriasis -> therapy_area LIKE '%Dermatology%'
   - Rheumatology / arthritis / lupus -> therapy_area LIKE '%Rheumatology%'
5. Dosage routes & formulations:
   - Oral / tablet / capsule -> (dosage LIKE '%tablet%' OR dosage LIKE '%capsule%' OR dosage LIKE '%oral%' OR drug_name LIKE '%tablet%' OR drug_name LIKE '%capsule%')
   - Injectable / injection / infusion -> (dosage LIKE '%injection%' OR dosage LIKE '%infusion%' OR drug_name LIKE '%injection%' OR drug_name LIKE '%infusion%')
6. Clinical indications: when searching for a specific disease or condition, check indication column:
   - e.g. "breast cancer" -> (indication LIKE '%breast cancer%' OR clean_molecule LIKE '%breast cancer%')
7. Formulation types:
   - Combination / FDC -> (drug_name LIKE '%+%' OR drug_name LIKE '% / %' OR drug_name LIKE 'FDC of %' OR composition LIKE '%+%')
   - Single / Monotherapy -> (drug_name NOT LIKE '%+%' AND drug_name NOT LIKE '% / %' AND drug_name NOT LIKE 'FDC of %')
8. Multiple companies (comparisons):
   - e.g. "compare Novartis and Roche" -> company_std IN ('Novartis', 'Roche')
9. Threshold & Ranking queries (e.g. "companies with 5+ approvals in oncology in 2025" or "who has the most approvals in 2024"):
   Do NOT use GROUP BY or HAVING because the analytical layer needs all individual approval rows to display the full interactive table and calculate exact thresholds. Instead, filter by the therapy area, year, and/or dosage:
   e.g. "which company has 5+ approvals in oncology in 2025" -> SELECT * FROM approvals WHERE therapy_area = 'Oncology' AND approval_year = 2025 ORDER BY approval_date_iso DESC, id DESC LIMIT 2500
10. ORDER BY clause:
   - For historical, first approval, earliest clearance, origin, or launch date queries (e.g. "when was X approved", "first clearance for Y", "earliest approval", "when did X launch"): ORDER BY approval_date_iso ASC, id ASC LIMIT 2500
   - For all other queries: ORDER BY approval_date_iso DESC, id DESC LIMIT 2500
11. Only generate read-only SELECT statements. Never generate UPDATE, DELETE, DROP, or INSERT.
"""

def is_natural_language_human_query(q):
    """Detects if query is a natural language question or complex phrase requiring generative interpretation."""
    if not q:
        return False
    q_str = q.strip().lower()
    if "?" in q:
        return True
    
    triggers = [
        "is there", "are there", "which", "what", "who", "compare", "versus", " vs ",
        "difference", "how many", "count of", "tell me", "can you", "list all", "show me",
        "approved for", "5+", "10+", "top ", "highest", "most", "lowest", "least",
        "oral ", "injectable", "iv ", "subcutaneous", "infusion", "inhalation",
        "breast cancer", "lung cancer", "leukemia", "lymphoma", "prostate cancer",
        "renal", "first approved", "when was", "when were"
    ]
    return any(t in q_str for t in triggers)

def execute_llm_text_to_sql(user_query, conn, limit=2500):
    """Generative NLP-to-SQL powered by Google Gemini 3.8 Flash with multi-model fallback."""
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as ef:
                for line in ef:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip().strip("'\"")
        except Exception:
            pass

    api_key = (
        os.environ.get("GEMINI_API_KEY") or
        os.environ.get("GOOGLE_API_KEY") or
        os.environ.get("GROQ_API_KEY") or
        os.environ.get("OPENAI_API_KEY") or
        os.environ.get("API_KEY")
    )
    if not api_key:
        return None, "NO_API_KEY"

    sql = None
    used_model = None

    # 1. Google Gemini API with multi-model fallback
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or api_key.startswith("AIza") or api_key.startswith("AQ"):
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or api_key
        gemini_models = [GEMINI_PRIMARY_MODEL] + [m for m in GEMINI_FALLBACK_MODELS if m != GEMINI_PRIMARY_MODEL]
        last_err = None
        for g_model in gemini_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{g_model}:generateContent"
            payload = {
                "contents": [{
                    "parts": [{"text": f"{SCHEMA_PROMPT}\n\nUser Question: {user_query}\nSQL Query:"}]
                }],
                "generationConfig": {"temperature": 0.0, "maxOutputTokens": 1024}
            }
            try:
                headers = {"Content-Type": "application/json", "x-goog-api-key": key}
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=6) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    raw_text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    cleaned = re.sub(r"^```(?:sql)?\s*", "", raw_text, flags=re.IGNORECASE).strip()
                    cleaned = re.sub(r"\s*```$", "", cleaned).strip()
                    cleaned = cleaned.strip().strip('"\'`').strip()
                    cleaned = cleaned.rstrip(";").strip()
                    select_match = re.search(r'(SELECT\s+[\s\S]+)', cleaned, re.IGNORECASE)
                    if select_match:
                        cleaned = select_match.group(1).strip()
                    if cleaned:
                        sql = cleaned
                        used_model = g_model
                        print(f"[Gemini] Successfully translated via {g_model}: {sql}")
                        break
            except Exception as e:
                last_err = str(e)
                continue
        if not sql and last_err:
            return None, f"GEMINI_ERROR: {last_err}"

    # 2. Groq API (Free tier fallback if configured)
    elif os.environ.get("GROQ_API_KEY") or api_key.startswith("gsk_"):
        key = os.environ.get("GROQ_API_KEY") or api_key
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SCHEMA_PROMPT},
                {"role": "user", "content": user_query}
            ],
            "temperature": 0.0,
            "max_tokens": 450
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}"
            })
            with urllib.request.urlopen(req, timeout=8) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                raw_text = res_data["choices"][0]["message"]["content"].strip()
                cleaned = re.sub(r"^```(?:sql)?\s*", "", raw_text, flags=re.IGNORECASE).strip()
                cleaned = re.sub(r"\s*```$", "", cleaned).strip()
                cleaned = cleaned.strip().strip('"\'`').strip()
                cleaned = cleaned.rstrip(";").strip()
                sql = cleaned
                used_model = "llama-3.3-70b-versatile"
        except Exception as e:
            return None, f"GROQ_ERROR: {str(e)}"

    if not sql:
        return None, "NO_SQL_GENERATED"

    # Security Guardrails
    sql_upper = sql.upper().strip()
    if not sql_upper.startswith("SELECT"):
        return None, "INVALID_QUERY_NON_SELECT"
    
    forbidden_terms = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "ATTACH", "DETACH", "PRAGMA"]
    if any(re.search(r'\b' + term + r'\b', sql_upper) for term in forbidden_terms):
        return None, "FORBIDDEN_KEYWORD"

    # Append LIMIT if missing to prevent unbounded queries
    if "LIMIT" not in sql_upper:
        sql += f" LIMIT {limit}"

    # Execute SQLite query safely
    try:
        c = conn.cursor()
        c.execute(sql)
        rows = c.fetchall()
        status_msg = f"SUCCESS_{used_model or 'GEMINI_3_8_FLASH'}"
        return rows, status_msg
    except Exception as e:
        print(f"[Gemini 3.8 Flash] SQLite Execution Error: {e} | SQL was: {sql}")
        return None, f"SQL_EXEC_ERROR: {str(e)}"


def execute_llm_grounded_synthesis(user_query, results, parsed):
    """
    Synthesizes an authoritative, executive regulatory response using Gemini,
    STRICTLY and EXCLUSIVELY grounded in the provided CDSCO database records.
    """
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as ef:
                for line in ef:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip().strip("'\"")
        except Exception:
            pass

    api_key = (
        os.environ.get("GEMINI_API_KEY") or
        os.environ.get("GOOGLE_API_KEY") or
        os.environ.get("GROQ_API_KEY") or
        os.environ.get("API_KEY")
    )
    if not api_key:
        return None, "NO_API_KEY"

    total_count = len(results)
    if not results:
        evidence = {
            "total_matches_in_database": 0,
            "status": "No verified CDSCO drug clearances matched the search criteria in the 2018–2026 digital registry."
        }
    else:
        comp_counts = Counter(r.get("company_std") or r.get("company") or "Unspecified" for r in results)
        ta_counts = Counter(r.get("therapy_area") or "Other" for r in results)
        biologic_count = sum(1 for r in results if r.get("molecule_type") == "Biologic")
        small_mol_count = sum(1 for r in results if r.get("molecule_type") == "Small Molecule")
        mono_count = sum(1 for r in results if r.get("formulation_type") == "Monotherapy")
        fdc_count = sum(1 for r in results if r.get("formulation_type") == "Combination (FDC)")

        evidence = {
            "total_clearances_found": total_count,
            "breakdown_molecule_type": {
                "biologics": biologic_count,
                "small_molecules": small_mol_count
            },
            "breakdown_therapy_structure": {
                "monotherapy": mono_count,
                "combination_fdc": fdc_count
            },
            "leading_manufacturers": dict(comp_counts.most_common(5)),
            "therapy_areas": dict(ta_counts.most_common(5))
        }

    grounding_system = (
        "You are CDSCO Intel, an authoritative and objective AI regulatory affairs intelligence analyst for the "
        "official Indian Central Drugs Standard Control Organisation (CDSCO) clearance registry (2018–2026).\n\n"
        "YOUR OBJECTIVE:\n"
        "Generate a direct, accurate, and beautifully formatted executive response to the user's query STRICTLY AND EXCLUSIVELY grounded "
        "in the provided CDSCO database records below.\n\n"
        "MANDATORY GROUNDING & FORMATTING RULES:\n"
        "1. STRICT DATABASE GROUNDING: Every single fact, number, date, company, molecule, and indication MUST come directly "
        "from the provided database records. NEVER hallucinate, extrapolate, or mention external approvals (such as US FDA or EMA) "
        "unless explicitly present in the CDSCO dataset.\n"
        "2. DIRECT ANSWER FIRST: Begin with a direct, comprehensive 1-2 sentence executive answer to the user's exact question.\n"
        "3. STRUCTURED SECTION HEADINGS: Always prefix section headings with standard markdown `### ` (e.g. `### Regulatory Overview`, `### Key Therapy Areas`, `### Leading Manufacturers`). NEVER output bare text lines as headings.\n"
        "4. CLEAN BULLET LISTS: Format lists cleanly with bullet points (`• **Metric**: Value`) or numbered lists (1., 2., 3.). Do not insert multiple blank lines between bullets.\n"
        "5. NO SAMPLE CLEARANCES TABLE: Absolutely DO NOT output any sample clearances table, individual clearance lists, or filing examples. The user already has the complete, interactive, filterable data table directly below. Keep your response strictly focused on the Regulatory Overview, Molecule Classifications, and Leading Manufacturers.\n"
        "6. ACCURATE AUDIT METRICS: Quote exact clearance counts, approval dates (DD-MON-YYYY format), and standardized company names.\n"
        "7. OUT-OF-SCOPE / NO RECORDS: If no records match, authoritatively explain that based on the official CDSCO "
        "registry (2018–2026), no clearances match the query.\n"
        "8. ZERO EMOJIS: Do NOT include cartoon emojis in headings, bullets, or body text. Maintain a calm, authoritative executive regulatory research tone."
    )

    prompt_text = (
        f"User Query: {user_query}\n\n"
        f"Verified CDSCO Database Records (Audit Evidence):\n"
        f"{json.dumps(evidence, indent=2)}\n\n"
        "Synthesize an authoritative, grounded regulatory response:"
    )

    gemini_models = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.8-flash"]
    full_prompt = f"{grounding_system}\n\n{prompt_text}"
    for g_model in gemini_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{g_model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 600}
        }
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=8) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                ans_text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                if ans_text:
                    # Strip any accidental Sample Clearances section
                    ans_text = re.split(r'###?\s*Sample\s+Clearances', ans_text, flags=re.IGNORECASE)[0].strip()
                    print(f"[Gemini Synthesis] Successfully synthesized via {g_model}")
                    return ans_text, g_model
        except Exception as e:
            print(f"[Gemini Synthesis] Model {g_model} failed: {e}")
            continue

    return None, "ALL_MODELS_UNAVAILABLE"


def generate_analytical_summary(query, parsed, results):
    """
    Directly and factually answers analytical, ranking, and statistical questions
    based on verified CDSCO clearance registry records.
    Returns tuple: (summary_text, filtered_results_list)
    """
    if not results:
        return None

    q_lower = query.lower()
    total = len(results)
    year = parsed.get("year")
    ta = parsed.get("therapy_area")
    comp = parsed.get("company")
    mol_type = parsed.get("molecule_type")
    
    # Scope string for clean narrative
    scope_desc = f"in {year}" if year else ("in " + ta if ta else "across the CDSCO registry (2018–2026)")

    # Extract numerical threshold if present
    min_threshold = parsed.get("min_threshold")
    if min_threshold is None:
        thresh_match = (
            re.search(r'\b(\d+)\s*\+', query) or
            re.search(r'(?:at\s*least|minimum\s*of|>=|more\s*than|>)\s*(\d+)', query, re.IGNORECASE) or
            re.search(r'(\d+)\s*(?:or\s*more|and\s*above)', query, re.IGNORECASE)
        )
        if thresh_match:
            min_threshold = int(thresh_match.group(1))

    intent = parsed.get("analytical_intent")
    
    # If not explicitly tagged, infer from query text
    if not intent:
        if any(w in q_lower for w in ["therapy area", "therapy areas", "therapeutic area", "disease area"]) and any(w in q_lower for w in ["highest", "most", "top", "leading", "best", "maximum", "largest", "rank", "which", "what"]):
            intent = "top_ta"
        elif any(w in q_lower for w in ["company", "companies", "manufacturer", "manufacturers", "applicant", "applicants", "firm", "firms", "who"]) and (min_threshold is not None or any(w in q_lower for w in ["highest", "most", "top", "leading", "best", "maximum", "largest", "rank", "which", "who", "what"])):
            intent = "top_comp"
        elif any(w in q_lower for w in ["how many", "total number", "count of", "number of approvals", "number of drugs"]):
            intent = "count"

    if not intent:
        return None

    if intent == "top_ta":
        ta_counts = Counter(r.get("therapy_area") or "Other" for r in results)
        top_tas = ta_counts.most_common(5)
        if not top_tas:
            return None
        top_ta, top_count = top_tas[0]
        top_pct = round((top_count / total) * 100, 1) if total else 0
        
        ta_items = []
        for idx, (t_name, cnt) in enumerate(top_tas, 1):
            pct = round((cnt / total) * 100, 1)
            mol_counts = Counter(r.get("clean_molecule") for r in results if r.get("therapy_area") == t_name and r.get("clean_molecule"))
            top_mols = [m for m, _ in mol_counts.most_common(3)]
            mol_str = f" — *Key molecules: {', '.join(top_mols)}*" if top_mols else ""
            ta_items.append(f"{idx}. **{t_name}**: **{cnt} approvals** ({pct}%){mol_str}")
            
        sm_cnt = sum(1 for r in results if r.get("molecule_type") == "Small Molecule")
        bio_cnt = sum(1 for r in results if r.get("molecule_type") == "Biologic")
        top_comps = Counter(r.get("company_std") or r.get("company") for r in results if r.get("company_std") or r.get("company")).most_common(3)
        comp_str = ", ".join([f"**{c[0]}** ({c[1]})" for c in top_comps])
        
        items_text = "\n".join(ta_items)
        summary = (
            f"In **{year or 'the CDSCO registry'}**, **{top_ta}** recorded the highest number of CDSCO drug clearances with **{top_count} approvals** (~{top_pct}% of all clearances {scope_desc}).\n\n"
            f"**Top Therapy Areas {scope_desc.capitalize() if not scope_desc.startswith('in') else 'in ' + str(year or 'Registry')}:**\n"
            f"{items_text}\n\n"
            f"Across all clinical areas {scope_desc}, CDSCO granted **{total} total clearances** ({sm_cnt} Small Molecule, {bio_cnt} Biologic). Leading manufacturers in this period were {comp_str}."
        )
        return summary, results

    elif intent == "top_comp":
        comp_counts = Counter(r.get("company_std") or r.get("company") or "Unspecified" for r in results)
        
        scope_prefix = f"in **{ta}**" if ta else ""
        year_prefix = f"in **{year}**" if year else ""
        context_str = f"{scope_prefix} {year_prefix}".strip()
        if not context_str:
            context_str = "across the CDSCO registry (2018–2026)"

        # Threshold-based filtering (e.g. 5+ approvals)
        if min_threshold is not None:
            qualifying_comps = [(c, cnt) for c, cnt in comp_counts.most_common() if cnt >= min_threshold and c != "Unspecified"]
            
            if not qualifying_comps:
                top_overall = comp_counts.most_common(1)
                lead_str = f" The leading manufacturer was **{top_overall[0][0]}** with **{top_overall[0][1]} approvals**." if top_overall else ""
                summary = (
                    f"No pharmaceutical company received **{min_threshold}+ approvals** {context_str}.{lead_str}\n\n"
                    f"Total verified clearances {scope_desc}: **{total}**."
                )
                return summary, results
            
            qual_names = {c[0] for c in qualifying_comps}
            comp_word = "company" if len(qualifying_comps) == 1 else "companies"
            
            company_items = []
            for idx, (c_name, cnt) in enumerate(qualifying_comps, 1):
                pct = round((cnt / total) * 100, 1)
                mol_counts = Counter(r.get("clean_molecule") for r in results if (r.get("company_std") == c_name or r.get("company") == c_name) and r.get("clean_molecule"))
                top_mols = [m for m, _ in mol_counts.most_common(3)]
                mol_str = f" — *Key molecules: {', '.join(top_mols)}*" if top_mols else ""
                company_items.append(f"{idx}. **{c_name}**: **{cnt} approvals** ({pct}%){mol_str}")
            
            items_text = "\n".join(company_items)
            summary = (
                f"There are **{len(qualifying_comps)} pharmaceutical {comp_word}** with **{min_threshold}+ CDSCO clearances** {context_str}:\n\n"
                f"**Manufacturers with {min_threshold}+ Approvals ({scope_desc}):**\n"
                f"{items_text}\n\n"
                f"Total verified clearances across all manufacturers {scope_desc}: **{total}**."
            )
            filtered_results = [r for r in results if (r.get("company_std") or r.get("company")) in qual_names]
            return summary, filtered_results

        # Standard ranking without numerical threshold
        top_comps = comp_counts.most_common(5)
        if not top_comps:
            return None
        top_c, top_count = top_comps[0]
        top_pct = round((top_count / total) * 100, 1) if total else 0
        
        company_items = []
        for idx, (c_name, cnt) in enumerate(top_comps, 1):
            pct = round((cnt / total) * 100, 1)
            mol_counts = Counter(r.get("clean_molecule") for r in results if (r.get("company_std") == c_name or r.get("company") == c_name) and r.get("clean_molecule"))
            top_mols = [m for m, _ in mol_counts.most_common(3)]
            mol_str = f" — *Key molecules: {', '.join(top_mols)}*" if top_mols else ""
            company_items.append(f"{idx}. **{c_name}**: **{cnt} approvals** ({pct}%){mol_str}")
            
        items_text = "\n".join(company_items)
        summary = (
            f"**{top_c}** led with the highest number of CDSCO clearances {scope_desc} with **{top_count} approvals** (~{top_pct}% of the total).\n\n"
            f"**Leading Manufacturers ({scope_desc}):**\n"
            f"{items_text}\n\n"
            f"Total verified clearances {scope_desc}: **{total}**."
        )
        return summary, results

    elif intent == "count":
        sm_count = sum(1 for r in results if r.get("molecule_type") == "Small Molecule")
        bio_count = sum(1 for r in results if r.get("molecule_type") == "Biologic")
        mono_count = sum(1 for r in results if r.get("formulation_type") == "Monotherapy")
        fdc_count = sum(1 for r in results if r.get("formulation_type") == "Combination (FDC)")
        
        lines = [
            f"CDSCO granted **{total} verified drug clearances** {scope_desc}.",
            f"• **Molecule Classification**: **{sm_count} Small Molecules** and **{bio_count} Biologics**.",
            f"• **Therapy Structure**: **{mono_count} Monotherapies** (Single Molecule) and **{fdc_count} Fixed-Dose Combinations** (FDC)."
        ]
        top_tas = Counter(r.get("therapy_area") for r in results if r.get("therapy_area")).most_common(3)
        if top_tas and not ta:
            lines.append(f"• **Top Therapy Areas**: " + ", ".join([f"**{t[0]}** ({t[1]})" for t in top_tas]) + ".")
        top_comps = Counter(r.get("company_std") or r.get("company") for r in results if r.get("company_std") or r.get("company")).most_common(3)
        if top_comps and not comp:
            lines.append(f"• **Leading Applicants**: " + ", ".join([f"**{c[0]}** ({c[1]})" for c in top_comps]) + ".")
        return "\n\n".join(lines), results

    return None

async def search_endpoint(request):
    start_time = time.time()
    query = request.query_params.get("q", "").strip()
    client_id = request.query_params.get("client_id") or request.headers.get("x-client-id") or "anonymous"
    ta_filter = request.query_params.get("ta", "").strip()
    year_filter = request.query_params.get("year", "").strip()
    cat_filter = request.query_params.get("cat", "").strip()
    comp_filter = request.query_params.get("comp", "").strip()
    mol_filter = request.query_params.get("mol_type", "").strip()
    form_filter = request.query_params.get("form_type", "").strip()
    raw_sort = request.query_params.get("sort", "").strip()

    # Allow full results (e.g. 575 in 2026, 615 in 2025, 1023 in 2022) without arbitrary 100-result truncation
    limit = int(request.query_params.get("limit", 2500))
    if limit <= 100:
        limit = 2500

    parsed = parse_query_intent(query)
    is_refinement = False
    q_low = query.lower()

    # Detect historical / first launch query intent
    is_historical_q = bool(
        parsed.get("is_historical") or
        any(t in q_low for t in [
            "when was", "when were", "first approved", "first launch", "first launched",
            "earliest approval", "earliest clearance", "earliest launch", "earliest",
            "history", "launch date", "originator"
        ])
    )

    # Set sort order: ascending by calendar date for historical queries, descending for general browsing
    if raw_sort:
        sort_by = raw_sort
    elif is_historical_q:
        sort_by = "date_asc"
    else:
        sort_by = "date_desc"

    # Override with manual dropdowns if passed
    if ta_filter: parsed["therapy_area"] = ta_filter
    if year_filter:
        try: parsed["year"] = int(year_filter)
        except: pass
    if cat_filter: parsed["product_category"] = cat_filter
    if comp_filter: parsed["company"] = comp_filter
    if mol_filter: parsed["molecule_type"] = mol_filter
    if form_filter: parsed["formulation_type"] = form_filter

    conn = get_db()
    c = conn.cursor()

    conditions = []
    params = []

    # 1. Apply Therapy Area filter (matching exact or multi-tag occurrences)
    if parsed["therapy_area"]:
        conditions.append("(therapy_area = ? OR therapy_area LIKE ? OR therapy_area LIKE ? OR therapy_area LIKE ?)")
        params.extend([
            parsed["therapy_area"],
            f"{parsed['therapy_area']},%",
            f"%, {parsed['therapy_area']}",
            f"%, {parsed['therapy_area']},%"
        ])

    # 2. Apply Year filter
    if parsed["year"]:
        conditions.append("approval_year = ?")
        params.append(parsed["year"])

    # 3. Apply Category filter
    if parsed["product_category"]:
        conditions.append("product_category = ?")
        params.append(parsed["product_category"])

    # 4. Apply Company filter (using standardized or raw company)
    if parsed["company"]:
        conditions.append("(company_std = ? OR company LIKE ?)")
        params.extend([parsed["company"], f"%{parsed['company']}%"])

    # 5. Apply Molecule Type filter (Biologic vs Small Molecule)
    if parsed.get("molecule_type"):
        conditions.append("molecule_type = ?")
        params.append(parsed["molecule_type"])

    # 5b. Apply Formulation / Therapy Mode filter (Monotherapy vs Combination)
    # Note: formulation_type is computed at runtime, not stored in DB. Use drug_name patterns.
    if parsed.get("formulation_type"):
        if parsed["formulation_type"] == "Monotherapy":
            conditions.append("(drug_name NOT LIKE '%+%' AND (composition IS NULL OR composition NOT LIKE '%+%') AND drug_name NOT LIKE '% / %')")
        elif parsed["formulation_type"] == "Combination (FDC)":
            conditions.append("(drug_name LIKE '%+%' OR composition LIKE '%+%' OR drug_name LIKE '% / %')")

    # 6. Apply Precision Search for Drug/Molecule terms
    # IMPORTANT: Do NOT match indication text when searching for a molecule!
    # This prevents combination therapy indication text (e.g. "with Rituximab") from polluting results.
    if parsed["clean_text"] and len(parsed["clean_text"]) > 1:
        words = parsed["clean_text"].split()
        for w in words:
            if len(w) > 2:
                conditions.append("(clean_molecule LIKE ? OR drug_name LIKE ? OR brand_name LIKE ? OR composition LIKE ?)")
                params.extend([f"%{w}%", f"%{w}%", f"%{w}%", f"%{w}%"])

    # If query is purely conversational greeting or about query, bypass DB query
    rows = []
    did_you_mean = None
    used_llm = False
    llm_status = None

    # Priority 1: If query is a natural language human query, use Gemini Text-to-SQL first
    if is_natural_language_human_query(query) and not parsed.get("is_greeting"):
        llm_rows, llm_status = execute_llm_text_to_sql(query, conn, limit)
        if llm_rows is not None and len(llm_rows) > 0:
            rows = llm_rows
            used_llm = True

    if not rows and not parsed.get("is_greeting") and (conditions or (parsed["clean_text"] and len(parsed["clean_text"]) > 1) or parsed.get("analytical_intent")):
        sql = """
            SELECT id, form_id, division_id, drug_name, clean_molecule, brand_name,
                   company, company_std, composition, dosage, indication,
                   approval_date, approval_year, applied_for, therapy_area,
                   product_category, molecule_type, regulatory_type, approval_date_iso
            FROM approvals
        """
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        order_parts = []
        if parsed["clean_text"] and len(parsed["clean_text"]) > 1:
            first_kw = parsed["clean_text"].split()[0]
            order_parts.append("CASE WHEN clean_molecule LIKE ? THEN 0 WHEN drug_name LIKE ? THEN 1 WHEN brand_name LIKE ? THEN 2 ELSE 3 END")
            params.extend([f"%{first_kw}%", f"%{first_kw}%", f"%{first_kw}%"])

        # Handle explicit sort direction from UI or historical default
        if sort_by == "date_asc":
            order_parts.append("approval_date_iso ASC")
        elif sort_by == "date_desc":
            order_parts.append("approval_date_iso DESC")
        elif sort_by == "drug_asc":
            order_parts.append("drug_name ASC")
        else:
            order_parts.append("approval_date_iso DESC")
        
        sql += " ORDER BY " + ", ".join(order_parts) + " LIMIT ?"
        params.append(limit)

        c.execute(sql, params)
        rows = c.fetchall()

        # Fallback 1: Fuzzy spell-correction against known molecules if 0 rows found
        if not rows and parsed["clean_text"] and len(parsed["clean_text"]) >= 4 and not parsed["therapy_area"]:
            token = parsed["clean_text"].lower().strip()
            close_matches = difflib.get_close_matches(token, list(KNOWN_MOL_MAP.keys()), n=1, cutoff=0.70)
            if close_matches:
                corrected_mol = KNOWN_MOL_MAP[close_matches[0]]
                did_you_mean = corrected_mol
                corr_conds = []
                corr_params = []
                if parsed["year"]:
                    corr_conds.append("approval_year = ?")
                    corr_params.append(parsed["year"])
                corr_conds.append("(clean_molecule LIKE ? OR drug_name LIKE ?)")
                corr_params.extend([f"%{corrected_mol}%", f"%{corrected_mol}%"])
                corr_order = "approval_date_iso ASC" if sort_by == "date_asc" else "approval_date_iso DESC"
                corr_sql = f"""
                    SELECT id, form_id, division_id, drug_name, clean_molecule, brand_name,
                           company, company_std, composition, dosage, indication,
                           approval_date, approval_year, applied_for, therapy_area,
                           product_category, molecule_type, regulatory_type, approval_date_iso
                    FROM approvals WHERE {" AND ".join(corr_conds)}
                    ORDER BY {corr_order} LIMIT ?
                """
                corr_params.append(limit)
                c.execute(corr_sql, corr_params)
                corr_rows = c.fetchall()
                if corr_rows:
                    rows = corr_rows
                    parsed["clean_text"] = corrected_mol

        # Fallback 2: Indication search ONLY if 0 matches found on drug/molecule
        if not rows and parsed["clean_text"] and len(parsed["clean_text"]) > 2 and not parsed["therapy_area"]:
            fallback_conds = []
            fallback_params = []
            if parsed["year"]:
                fallback_conds.append("approval_year = ?")
                fallback_params.append(parsed["year"])
            fallback_conds.append("indication LIKE ?")
            fallback_params.append(f"%{parsed['clean_text']}%")
            fb_order = "approval_date_iso ASC" if sort_by == "date_asc" else "approval_date_iso DESC"
            fallback_sql = f"""
                SELECT id, form_id, division_id, drug_name, clean_molecule, brand_name,
                       company, company_std, composition, dosage, indication,
                       approval_date, approval_year, applied_for, therapy_area,
                       product_category, molecule_type, regulatory_type, approval_date_iso
                FROM approvals WHERE {" AND ".join(fallback_conds)}
                ORDER BY {fb_order} LIMIT ?
            """
            fallback_params.append(limit)
            c.execute(fallback_sql, fallback_params)
            rows = c.fetchall()

        # Fallback 3: LLM Text-to-SQL — only for queries with genuine pharmaceutical text
        # Skip LLM for pure junk, random symbols, or single-character queries
        alpha_content = re.sub(r'[^a-zA-Z]', '', query)
        looks_like_real_query = len(alpha_content) >= 3
        if not rows and query and looks_like_real_query:
            llm_rows, llm_status = execute_llm_text_to_sql(query, conn, limit)
            if llm_rows:
                rows = llm_rows
                used_llm = True

    # If historical query or date_asc requested, guarantee true chronological ascending order
    if (is_historical_q or sort_by == "date_asc") and rows:
        rows = sorted(rows, key=lambda x: (parse_date_tuple(get_row_val(x, "approval_date"), get_row_val(x, "approval_date_iso")), get_row_val(x, "id", 0)))

    results = []
    for r in rows:
        comp_name = r["company"] or ""
        is_mnc = any(mnc in comp_name.lower() for mnc in MNC_FIRMS)
        d_name = r["drug_name"] or ""
        comp_str = r["composition"] or ""
        clean_m = r["clean_molecule"] if "clean_molecule" in r.keys() else ""
        is_fdc = is_combination_formulation(d_name, comp_str, clean_m)
        formulation_type = "Combination (FDC)" if is_fdc else "Monotherapy"
        iso_val = r["approval_date_iso"] if "approval_date_iso" in r.keys() and r["approval_date_iso"] else parse_date_tuple(r["approval_date"])
        
        results.append({
            "id": r["id"],
            "form_id": r["form_id"],
            "division_id": r["division_id"],
            "drug_name": r["drug_name"],
            "clean_molecule": r["clean_molecule"],
            "brand_name": r["brand_name"],
            "company": comp_name,
            "company_std": r["company_std"] or comp_name,
            "is_mnc": is_mnc,
            "composition": r["composition"],
            "dosage": r["dosage"],
            "indication": r["indication"],
            "approval_date": r["approval_date"],
            "approval_date_iso": iso_val,
            "approval_year": r["approval_year"],
            "applied_for": r["applied_for"],
            "therapy_area": r["therapy_area"],
            "therapy_areas": [ta.strip() for ta in (r["therapy_area"] or "Other").split(",") if ta.strip()],
            "product_category": r["product_category"],
            "molecule_type": r["molecule_type"] or "Small Molecule",
            "formulation_type": formulation_type,
            "is_combination": is_fdc
        })

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    # Dynamic molecule intelligence & real-world market research ONLY for specific molecule/brand searches
    # Strictly exclude broad macro-category queries (years, molecule types, therapy areas, company portfolios, counts)
    q_low = query.lower()
    has_specific_mol = bool(parsed["clean_text"] or parsed.get("historical_match"))
    is_macro_query = (not has_specific_mol) or bool(
        (parsed["year"] and not parsed["clean_text"]) or
        (parsed["therapy_area"] and not parsed["clean_text"]) or
        (parsed["company"] and not parsed["clean_text"]) or
        (parsed.get("molecule_type") and not parsed["clean_text"]) or
        (parsed.get("analytical_intent") and not parsed["clean_text"]) or
        any(re.search(r'\b' + term + r'\b', q_low) for term in [
            "small molecule", "small molecules", "biologic", "biologics",
            "approvals in", "clearances in", "all drugs", "top companies", "highest approval",
            "which therapy", "most approvals", "all approvals", "all clearances",
            "approved molecules", "molecules in", "drugs in", "approvals for", "clearances for"
        ])
    )

    molecule_intel = None
    market_intel = None
    target_mol = None

    if not is_macro_query:
        candidate_mol = parsed["clean_text"] or (parsed.get("historical_match") or {}).get("molecule")
        
        # Check if candidate_mol or raw query matches an active pharmaceutical molecule in KNOWN_MOL_MAP / KNOWN_MOLECULES
        candidate_is_known_molecule = False
        if candidate_mol:
            c_low = candidate_mol.lower().strip()
            if c_low in KNOWN_MOL_MAP:
                candidate_mol = KNOWN_MOL_MAP[c_low]
                candidate_is_known_molecule = True
            else:
                for km_key, km_val in sorted(KNOWN_MOL_MAP.items(), key=lambda x: len(x[0]), reverse=True):
                    if re.search(r'\b' + re.escape(km_key) + r'\b', c_low):
                        candidate_mol = km_val
                        candidate_is_known_molecule = True
                        break

        # If not matched yet, check query text directly against KNOWN_MOL_MAP
        if not candidate_is_known_molecule:
            for km_key, km_val in sorted(KNOWN_MOL_MAP.items(), key=lambda x: len(x[0]), reverse=True):
                if re.search(r'\b' + re.escape(km_key) + r'\b', q_low):
                    candidate_mol = km_val
                    candidate_is_known_molecule = True
                    break

        # ONLY if the user did NOT search a recognized active substance, resolve if they searched a trade brand name
        if candidate_mol and not candidate_is_known_molecule and results:
            for r in results:
                b_name = (r.get("brand_name") or "").strip().lower()
                clean_m = (r.get("clean_molecule") or "").strip()
                if b_name and clean_m and not is_generic_brand_string(b_name, clean_m):
                    if candidate_mol.lower() == b_name or candidate_mol.lower() in b_name.split():
                        candidate_mol = clean_m
                        break

        # Validate that candidate_mol is a genuine recognized pharmaceutical molecule or commercial brand
        is_known_mol = False
        if candidate_mol and len(candidate_mol) >= 3:
            c_low = candidate_mol.lower().strip()
            if candidate_is_known_molecule or c_low in KNOWN_MOL_MAP or any(c_low == (m.lower() if m else '') for m in KNOWN_MOLECULES):
                is_known_mol = True
            elif results and any(c_low == (r.get("clean_molecule") or "").lower() for r in results):
                is_known_mol = True
            elif results and any(c_low == (r.get("brand_name") or "").lower() for r in results):
                is_known_mol = True

        # Only generate molecule intel & executive market intel if candidate is an authentic validated drug molecule
        if is_known_mol:
            target_mol = candidate_mol
            molecule_intel = get_dynamic_molecule_intelligence(conn, target_mol)
            market_intel = get_real_world_market_intelligence(target_mol)

    # Build conversational summary
    conversational_summary = None
    if results:
        total_count = len(results)
        comp_counts = {}
        ta_counts = {}
        formulation_count = sum(1 for r in results if r["product_category"] == "Finished Formulation")
        bulk_count = sum(1 for r in results if r["product_category"] == "Bulk API")
        biologic_count = sum(1 for r in results if r["molecule_type"] == "Biologic")
        small_mol_count = sum(1 for r in results if r["molecule_type"] == "Small Molecule")
        mono_count = sum(1 for r in results if r["formulation_type"] == "Monotherapy")
        fdc_count = sum(1 for r in results if r["formulation_type"] == "Combination (FDC)")
        
        for r in results:
            c_name = r["company_std"] or r["company"] or "Unspecified"
            comp_counts[c_name] = comp_counts.get(c_name, 0) + 1
            t_area = r["therapy_area"] or "Other"
            ta_counts[t_area] = ta_counts.get(t_area, 0) + 1

        top_companies = sorted(comp_counts.items(), key=lambda x: x[1], reverse=True)[:4]
        narrative_parts = []

        # Check for direct analytical / statistical question answering first
        analytical_res = generate_analytical_summary(query, parsed, results)
        if analytical_res:
            analytical_ans, filtered_results = analytical_res
            results = filtered_results
            if did_you_mean:
                analytical_ans = f"*(Auto-corrected search from \"{query}\" to **{did_you_mean}**)*\n\n" + analytical_ans
            if used_llm:
                analytical_ans += "\n\n*(Synthesized via generative Text-to-SQL layer)*"
            conversational_summary = analytical_ans
        elif is_historical_q:
            # If molecule_intel is available and has first_approval_date, harmonize with it 100%
            if molecule_intel and molecule_intel.get("first_approval_date"):
                earliest_date = molecule_intel["first_approval_date"]
                earliest_comp = molecule_intel.get("earliest_sugam_applicant") or molecule_intel.get("first_applicant") or "Registered Firm"
                mol_disp = molecule_intel.get("molecule") or candidate_mol or "this substance"
            else:
                kw = parsed["clean_text"].lower() if parsed["clean_text"] else ""
                exact_matches = [r for r in results if kw and kw in (r.get("clean_molecule") or r.get("drug_name") or "").lower()]
                pool = exact_matches if exact_matches else results
                earliest = sorted(pool, key=lambda x: (parse_date_tuple(x.get("approval_date"), x.get("approval_date_iso")), x.get("id", 0)))[0]
                earliest_date = earliest.get("approval_date")
                earliest_comp = earliest.get("company_std") or earliest.get("company")
                mol_disp = earliest.get("clean_molecule") or earliest.get("drug_name")

            narrative_parts.append(
                f"In the official **CDSCO SUGAM digital registry (2018–2026)**, the earliest recorded portal clearance for **{mol_disp}** was granted on **{earliest_date}** to **{earliest_comp}**."
            )
            narrative_parts.append(f" Across the modern registry, there are **{total_count} verified clearances** ({biologic_count} Biologic, {small_mol_count} Small Molecule).")
            if did_you_mean:
                narrative_parts.insert(0, f"*(Auto-corrected search from \"{query}\" to **{did_you_mean}**)*\n\n")
            conversational_summary = "".join(narrative_parts)
        elif used_llm and is_natural_language_human_query(query):
            # For complex natural language questions, synthesize concise 2-3 sentence answer via LLM
            llm_grounded_ans, synth_model = execute_llm_grounded_synthesis(query, results, parsed)
            if llm_grounded_ans:
                if did_you_mean:
                    llm_grounded_ans = f"*(Auto-corrected search from \"{query}\" to **{did_you_mean}**)*\n\n" + llm_grounded_ans
                conversational_summary = llm_grounded_ans
            else:
                q_disp = query.strip() if query.strip() else "your query"
                conversational_summary = f"Found **{total_count} verified CDSCO clearances** matching *\"{q_disp}\"* (2018–2026 registry)."
        else:
            # Clean, fast, deterministic 2-3 line executive summary
            q_disp = query.strip() if query.strip() else (parsed["company"] or parsed["therapy_area"] or "Indian Approvals")
            
            # Line 1: Primary match statement
            if parsed["company"] and not parsed["clean_text"] and not parsed["therapy_area"] and not parsed["year"]:
                narrative_parts.append(f"Found **{total_count} verified CDSCO clearances** for **{parsed['company']}** in the official 2018–2026 registry.")
            elif parsed["therapy_area"] and not parsed["clean_text"] and not parsed["company"]:
                yr_str = f" in **{parsed['year']}**" if parsed["year"] else ""
                narrative_parts.append(f"Found **{total_count} verified CDSCO clearances** in **{parsed['therapy_area']}**{yr_str} (2018–2026).")
            elif parsed["year"] and not parsed["clean_text"] and not parsed["company"] and not parsed["therapy_area"]:
                mol_str = f" for **{parsed['molecule_type']}s**" if parsed.get("molecule_type") else ""
                narrative_parts.append(f"Found **{total_count} verified CDSCO clearances**{mol_str} recorded for **{parsed['year']}** in the official registry.")
            elif parsed["clean_text"]:
                mol_label = results[0]["clean_molecule"] or parsed["clean_text"].title()
                narrative_parts.append(f"Found **{total_count} verified CDSCO clearances** for **{mol_label}** in the official 2018–2026 registry.")
            else:
                narrative_parts.append(f"Found **{total_count} verified CDSCO approvals** matching *\"{q_disp}\"* (2018–2026 registry).")

            # Line 2: Molecule type & therapy structure breakdown
            type_parts = []
            if small_mol_count > 0: type_parts.append(f"**{small_mol_count} Small Molecule**")
            if biologic_count > 0: type_parts.append(f"**{biologic_count} Biologic**")
            struct_parts = []
            if mono_count > 0: struct_parts.append(f"{mono_count} Monotherapy")
            if fdc_count > 0: struct_parts.append(f"{fdc_count} Fixed-Dose Combinations")
            
            struct_str = f" ({', '.join(struct_parts)})" if struct_parts else ""
            narrative_parts.append(f"• **Classification**: {', '.join(type_parts)}{struct_str}.")

            # Line 3: Clinical domain / Leaders
            if parsed["company"]:
                top_tas = sorted(ta_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                if top_tas:
                    ta_str = ", ".join([f"**{t[0]}** ({t[1]})" for t in top_tas])
                    narrative_parts.append(f"• **Key Therapy Areas**: {ta_str}.")
            elif parsed["therapy_area"]:
                if top_companies:
                    comp_str = ", ".join([f"**{c[0]}** ({c[1]})" for c in top_companies[:4]])
                    narrative_parts.append(f"• **Leading Manufacturers**: {comp_str}.")
            else:
                if top_companies:
                    comp_str = ", ".join([f"**{c[0]}** ({c[1]})" for c in top_companies[:3]])
                    narrative_parts.append(f"• **Leading Manufacturers**: {comp_str}.")

            if did_you_mean:
                narrative_parts.insert(0, f"*(Auto-corrected search from \"{query}\" to **{did_you_mean}**)*")

            conversational_summary = "\n".join(narrative_parts)
    else:
        if parsed.get("is_greeting"):
            conversational_summary = (
                "**Welcome to CDSCO Intel** — regulatory intelligence engine over official "
                "Indian drug approvals (2018–2026).\n\n"
                "**Supported query categories:**\n"
                "• **Molecule Dossiers**: e.g., *'Semaglutide'*, *'Ustekinumab'*, *'Rituximab'*\n"
                "• **Regulatory Classifications**: e.g., *'Innovator launches in 2026'*, *'Biosimilar approvals in India'*\n"
                "• **Manufacturer Pipelines**: e.g., *'Sun Pharma'*, *'Cipla'*, *'Dr. Reddy\'s'*, *'AstraZeneca'*\n"
                "• **Therapy Areas**: e.g., *'Oncology'*, *'Diabetology'*, *'Cardiology'*\n\n"
                "*Select a suggested query chip or enter an active molecule substance above.*"
            )
        elif not re.sub(r'[^a-zA-Z0-9]', '', query).strip():
            conversational_summary = (
                "Please enter a valid search term, such as an active drug substance (e.g. *Semaglutide*), "
                "brand name, applicant company (e.g. *Sun Pharma*), or clinical therapy area (*Oncology*)."
            )
        else:
            criteria = []
            if parsed["therapy_area"]: criteria.append(f"therapy area '{parsed['therapy_area']}'")
            if parsed["year"]: criteria.append(f"year {parsed['year']}")
            if parsed["company"]: criteria.append(f"company '{parsed['company']}'")
            if parsed["clean_text"]: criteria.append(f"molecule '{parsed['clean_text']}'")
            
            criteria_str = " + ".join(criteria) if criteria else query
            conversational_summary = f"No verified CDSCO approvals matched **{criteria_str}** in the official 2018–2026 registry."

    # Record search query in query_logs telemetry
    try:
        is_zero = 1 if len(results) == 0 and not parsed.get("is_greeting") else 0
        c.execute("""
            INSERT INTO query_logs (timestamp, client_id, query, parsed_ta, parsed_company, parsed_year, result_count, latency_ms, is_zero_result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(timezone.utc).isoformat(),
            client_id,
            query,
            parsed.get("therapy_area"),
            parsed.get("company"),
            parsed.get("year"),
            len(results),
            elapsed_ms,
            is_zero
        ))
        conn.commit()
    except Exception as log_err:
        print(f"[Query Log Error]: {log_err}")

    conn.close()

    return JSONResponse({
        "query": query,
        "is_refinement": is_refinement,
        "is_greeting": parsed.get("is_greeting", False),
        "sort_by": sort_by,
        "is_historical": is_historical_q,
        "did_you_mean": did_you_mean,
        "active_context": {
            "therapy_area": parsed["therapy_area"],
            "year": parsed["year"],
            "company": parsed["company"],
            "product_category": parsed["product_category"],
            "molecule_type": parsed.get("molecule_type"),
            "formulation_type": parsed.get("formulation_type")
        },
        "total_matches": len(results),
        "latency_ms": elapsed_ms,
        "ai_summary": conversational_summary,
        "historical_web_context": None,
        "molecule_intel": molecule_intel,
        "market_intelligence": market_intel,
        "suggested_followups": [],
        "results": results
    })


async def filters_metadata_endpoint(request):
    """Provides available dropdown filter options including top standardized companies."""
    conn = get_db()
    c = conn.cursor()

    # Top companies with >= 5 approvals
    c.execute("""
        SELECT company_std, COUNT(*) as cnt
        FROM approvals
        WHERE company_std IS NOT NULL AND company_std != 'Unknown'
        GROUP BY company_std
        HAVING cnt >= 5
        ORDER BY cnt DESC, company_std ASC
    """)
    companies = [{"name": r["company_std"], "count": r["cnt"]} for r in c.fetchall()]

    # Therapy areas
    c.execute("SELECT DISTINCT therapy_area FROM approvals WHERE therapy_area IS NOT NULL")
    raw_tas = c.fetchall()
    unique_tas = set()
    for r in raw_tas:
        for t in (r[0] or "").split(","):
            s = t.strip()
            if s:
                unique_tas.add(s)
    tas = sorted(list(unique_tas))

    # Years
    c.execute("SELECT DISTINCT approval_year FROM approvals WHERE approval_year IS NOT NULL AND approval_year > 0 ORDER BY approval_year DESC")
    years = [r[0] for r in c.fetchall()]

    conn.close()

    return JSONResponse({
        "companies": companies,
        "therapy_areas": tas,
        "years": years,
        "molecule_types": ["Biologic", "Small Molecule"],
        "formulation_types": ["Monotherapy", "Combination (FDC)"],
        "categories": ["Finished Formulation", "Bulk API"]
    })

async def suggestions_endpoint(request):
    """Computes dynamic suggestions from CDSCO data."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM approvals WHERE therapy_area = 'Oncology' AND approval_year = 2025")
    onco_2025 = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM approvals WHERE molecule_type = 'Biologic'")
    bio_cnt = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM approvals WHERE molecule_type = 'Small Molecule' AND approval_year = 2026")
    sm_2026 = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM approvals WHERE company_std = 'Sun Pharma'")
    sun_cnt = c.fetchone()[0]

    conn.close()

    suggestions = [
        {"icon": "dna", "label": f"Biologic Approvals ({bio_cnt} records)", "query": "Biologics approved in India"},
        {"icon": "pill", "label": f"Small Molecules in 2026 ({sm_2026} approvals)", "query": "Small molecules in 2026"},
        {"icon": "bolt", "label": f"Oncology in 2025 ({onco_2025} approvals)", "query": "Oncology 2025"},
        {"icon": "building", "label": f"Sun Pharma Clearances ({sun_cnt} records)", "query": "Sun Pharma approvals"},
        {"icon": "pill", "label": "Semaglutide Clearances", "query": "Semaglutide"},
        {"icon": "layers", "label": "Vildagliptin Monotherapy vs Combinations", "query": "Vildagliptin"},
        {"icon": "dna", "label": "Ustekinumab Biologics", "query": "Ustekinumab"}
    ]
    return JSONResponse({"suggestions": suggestions})

async def stats_endpoint(request):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM approvals")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM approvals WHERE product_category = 'Finished Formulation'")
    formulations = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM approvals WHERE product_category = 'Bulk API'")
    bulk = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM approvals WHERE molecule_type = 'Biologic'")
    biologics = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM approvals WHERE molecule_type = 'Small Molecule'")
    small_molecules = c.fetchone()[0]

    c.execute("SELECT therapy_area FROM approvals WHERE therapy_area IS NOT NULL")
    all_tas = []
    for r in c.fetchall():
        for ta in (r["therapy_area"] or "").split(","):
            t = ta.strip()
            if t:
                all_tas.append(t)
    ta_counts = Counter(all_tas)
    ta_stats = [{"name": name, "count": cnt} for name, cnt in ta_counts.most_common()]

    conn.close()
    return JSONResponse({
        "total_approvals": total,
        "formulations": formulations,
        "bulk_apis": bulk,
        "biologics": biologics,
        "small_molecules": small_molecules,
        "years_covered": "2018 – 2026",
        "last_sync": "September 2026",
        "therapy_areas": ta_stats
    })

async def model_info_endpoint(request):
    """Returns the active AI model configuration verifying Gemini 3.8 Flash."""
    api_key_set = bool(
        os.environ.get("GEMINI_API_KEY") or
        os.environ.get("GOOGLE_API_KEY") or
        os.environ.get("GROQ_API_KEY")
    )
    return JSONResponse({
        "provider": "Google Gemini",
        "primary_model": GEMINI_PRIMARY_MODEL,
        "supported_models": [GEMINI_PRIMARY_MODEL] + GEMINI_FALLBACK_MODELS,
        "api_key_configured": api_key_set,
        "architecture": "Google DeepMind Generative Language API (v1beta)",
        "nlp_text_to_sql": "Active" if api_key_set else "Awaiting Key"
    })

async def telemetry_endpoint(request):
    try:
        data = await request.json()
        event_name = data.get("event") or "unknown"
        client_id = data.get("distinct_id") or data.get("client_id") or "anonymous"
        timestamp = data.get("timestamp") or datetime.now(timezone.utc).isoformat()
        properties = json.dumps(data.get("properties") or {})

        conn = get_db()
        c = conn.cursor()
        c.execute("""
            INSERT INTO telemetry_events (timestamp, client_id, event_type, metadata_json)
            VALUES (?, ?, ?, ?)
        """, (timestamp, client_id, event_name, properties))
        conn.commit()
        conn.close()
        return JSONResponse({"status": "ok"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

async def analytics_endpoint(request):
    try:
        conn = get_db()
        c = conn.cursor()

        # 1. Unique visitors
        c.execute("""
            SELECT COUNT(DISTINCT client_id) FROM (
                SELECT client_id FROM query_logs WHERE client_id IS NOT NULL AND client_id != ''
                UNION
                SELECT client_id FROM telemetry_events WHERE client_id IS NOT NULL AND client_id != ''
            )
        """)
        unique_visitors = c.fetchone()[0] or 1

        # 2. Total queries & average
        c.execute("SELECT COUNT(*) FROM query_logs")
        total_queries = c.fetchone()[0] or 0
        avg_queries_per_visitor = round(total_queries / max(unique_visitors, 1), 1)

        # 3. Average latency
        c.execute("SELECT AVG(latency_ms) FROM query_logs")
        avg_lat = c.fetchone()[0] or 0.0
        avg_latency_ms = round(float(avg_lat), 1)

        # 4. Zero match queries & rate
        c.execute("SELECT COUNT(*) FROM query_logs WHERE is_zero_result = 1")
        zero_match_count = c.fetchone()[0] or 0
        zero_match_rate = round((zero_match_count / max(total_queries, 1)) * 100, 1)

        # 5. Deliverable actions (Excel & Slides)
        c.execute("SELECT COUNT(*) FROM telemetry_events WHERE event_type IN ('excel_exported', 'exported_csv')")
        excel_exports = c.fetchone()[0] or 0

        c.execute("SELECT COUNT(*) FROM telemetry_events WHERE event_type IN ('slides_copied', 'table_copied_for_slides')")
        slides_copies = c.fetchone()[0] or 0

        total_deliverables = excel_exports + slides_copies

        # 6. Dossier drill-downs
        c.execute("SELECT COUNT(*) FROM telemetry_events WHERE event_type IN ('dossier_opened', 'drug_detail_opened')")
        dossier_views = c.fetchone()[0] or 0

        # 7. Top search queries
        c.execute("""
            SELECT query, COUNT(*) as cnt
            FROM query_logs
            WHERE query IS NOT NULL AND TRIM(query) != ''
            GROUP BY LOWER(TRIM(query))
            ORDER BY cnt DESC
            LIMIT 7
        """)
        top_queries = [{"query": r["query"], "count": r["cnt"]} for r in c.fetchall()]

        # 8. Top therapy areas searched
        c.execute("""
            SELECT parsed_ta, COUNT(*) as cnt
            FROM query_logs
            WHERE parsed_ta IS NOT NULL AND TRIM(parsed_ta) != ''
            GROUP BY parsed_ta
            ORDER BY cnt DESC
            LIMIT 5
        """)
        top_tas = [{"therapy_area": r["parsed_ta"], "count": r["cnt"]} for r in c.fetchall()]

        # 9. Top companies searched
        c.execute("""
            SELECT parsed_company, COUNT(*) as cnt
            FROM query_logs
            WHERE parsed_company IS NOT NULL AND TRIM(parsed_company) != ''
            GROUP BY parsed_company
            ORDER BY cnt DESC
            LIMIT 5
        """)
        top_companies = [{"company": r["parsed_company"], "count": r["cnt"]} for r in c.fetchall()]

        # 10. Unmet Search Demand (Zero-Result Queries)
        c.execute("""
            SELECT query, COUNT(*) as cnt, MAX(timestamp) as last_seen
            FROM query_logs
            WHERE is_zero_result = 1 AND query IS NOT NULL AND TRIM(query) != ''
            GROUP BY LOWER(TRIM(query))
            ORDER BY cnt DESC, last_seen DESC
            LIMIT 6
        """)
        zero_result_queries = [
            {"query": r["query"], "count": r["cnt"], "last_seen": r["last_seen"]}
            for r in c.fetchall()
        ]

        # 11. Recent Search Activity Feed
        c.execute("""
            SELECT timestamp, query, result_count, latency_ms, is_zero_result
            FROM query_logs
            ORDER BY id DESC
            LIMIT 12
        """)
        recent_queries = [
            {
                "timestamp": r["timestamp"],
                "query": r["query"],
                "result_count": r["result_count"],
                "latency_ms": round(float(r["latency_ms"] or 0), 1),
                "is_zero_result": bool(r["is_zero_result"])
            }
            for r in c.fetchall()
        ]

        conn.close()

        return JSONResponse({
            "kpis": {
                "unique_visitors": unique_visitors,
                "total_queries": total_queries,
                "avg_queries_per_visitor": avg_queries_per_visitor,
                "avg_latency_ms": avg_latency_ms,
                "zero_match_count": zero_match_count,
                "zero_match_rate": zero_match_rate,
                "total_deliverables": total_deliverables,
                "excel_exports": excel_exports,
                "slides_copies": slides_copies,
                "dossier_views": dossier_views
            },
            "top_queries": top_queries,
            "top_therapy_areas": top_tas,
            "top_companies": top_companies,
            "zero_result_queries": zero_result_queries,
            "recent_queries": recent_queries,
            "generated_at": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

async def index_page(request):
    res = FileResponse("public/index.html")
    res.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    res.headers["Pragma"] = "no-cache"
    res.headers["Expires"] = "0"
    return res

class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/static") or request.url.path == "/":
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

routes = [
    Route("/", endpoint=index_page),
    Route("/api/search", endpoint=search_endpoint),
    Route("/api/filters", endpoint=filters_metadata_endpoint),
    Route("/api/stats", endpoint=stats_endpoint),
    Route("/api/suggestions", endpoint=suggestions_endpoint),
    Route("/api/model-info", endpoint=model_info_endpoint),
    Route("/api/telemetry", endpoint=telemetry_endpoint, methods=["POST"]),
    Route("/api/analytics", endpoint=analytics_endpoint, methods=["GET"]),
    Mount("/static", app=StaticFiles(directory="public"), name="static")
]

app = Starlette(debug=os.environ.get("DEBUG", "false").lower() == "true", routes=routes, middleware=[Middleware(NoCacheMiddleware)])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"Starting CDSCO Intel Regulatory Engine on {host}:{port}...")
    uvicorn.run(app, host=host, port=port)
