import sqlite3
import json
import re

DB_PATH = "cdsco_approvals.db"

# Comprehensive company standardization mapping
COMPANY_MAP = {
    # Top MNCs
    "astrazeneca": "AstraZeneca",
    "roche": "Roche",
    "novartis": "Novartis",
    "pfizer": "Pfizer",
    "sanofi": "Sanofi",
    "msd": "MSD Pharma",
    "merck sharp": "MSD Pharma",
    "merck specialities": "Merck Group",
    "merck healthcare": "Merck Group",
    "johnson & johnson": "Johnson & Johnson",
    "janssen": "Johnson & Johnson",
    "eli lilly": "Eli Lilly",
    "lilly": "Eli Lilly",
    "abbott": "Abbott",
    "bayer": "Bayer",
    "boehringer": "Boehringer Ingelheim",
    "novo nordisk": "Novo Nordisk",
    "takeda": "Takeda",
    "amgen": "Amgen",
    "bristol-myers": "Bristol Myers Squibb",
    "bristol myers": "Bristol Myers Squibb",
    "bms": "Bristol Myers Squibb",
    "gilead": "Gilead Sciences",
    "ferring": "Ferring Pharmaceuticals",
    "astellas": "Astellas Pharma",
    "daiichi": "Daiichi Sankyo",
    "otsuka": "Otsuka Pharmaceutical",
    "gsk": "GlaxoSmithKline",
    "glaxo": "GlaxoSmithKline",
    "servier": "Servier",

    # Top Indian Pharma Majors
    "dr. reddy": "Dr. Reddy's Laboratories",
    "dr reddy": "Dr. Reddy's Laboratories",
    "sun pharma": "Sun Pharma",
    "sun pharmaceutical": "Sun Pharma",
    "cipla": "Cipla",
    "zydus": "Zydus Lifesciences",
    "cadila healthcare": "Zydus Lifesciences",
    "lupin": "Lupin",
    "mankind": "Mankind Pharma",
    "hetero": "Hetero Labs",
    "torrent": "Torrent Pharma",
    "intas": "Intas Pharmaceuticals",
    "alkem": "Alkem Laboratories",
    "biocon": "Biocon",
    "natco": "Natco Pharma",
    "glenmark": "Glenmark Pharmaceuticals",
    "eris": "Eris Lifesciences",
    "mylan": "Viatris / Mylan",
    "viatris": "Viatris / Mylan",
    "ajanta": "Ajanta Pharma",
    "alembic": "Alembic Pharmaceuticals",
    "ipca": "Ipca Laboratories",
    "micro labs": "Micro Labs",
    "emcure": "Emcure Pharmaceuticals",
    "wockhardt": "Wockhardt",
    "panacea": "Panacea Biotec",
    "serum institute": "Serum Institute of India",
    "bharat biotech": "Bharat Biotech",
    "biological e": "Biological E",
    "windlas": "Windlas Biotech",
    "msn laboratories": "MSN Laboratories",
    "msn organics": "MSN Laboratories",
    "pure & cure": "Pure & Cure Healthcare",
    "akums": "Akums Drugs & Pharmaceuticals",
    "macleods": "Macleods Pharmaceuticals",
    "aristo": "Aristo Pharmaceuticals",
    "usv": "USV Private Limited",
    "indoco": "Indoco Remedies",
    "suven": "Suven Pharmaceuticals",
    "laurus": "Laurus Labs",
    "gland": "Gland Pharma",
    "troikaa": "Troikaa Pharmaceuticals",
    "piramal": "Piramal Healthcare"
}

# Known global innovators for landmark molecules
KNOWN_INNOVATORS = {
    "trastuzumab deruxtecan": ["astrazeneca", "daiichi sankyo", "daiichi"],
    "trastuzumab emtansine": ["roche", "genentech"],
    "datopotamab deruxtecan": ["astrazeneca", "daiichi sankyo", "daiichi"],
    "rituximab": ["roche", "nicholas piramal", "genentech", "chugai"],
    "trastuzumab": ["roche", "genentech"],
    "bevacizumab": ["roche", "genentech"],
    "adalimumab": ["abbvie", "abbott"],
    "ustekinumab": ["johnson & johnson", "janssen"],
    "pembrolizumab": ["msd", "merck"],
    "nivolumab": ["bristol-myers", "bms"],
    "durvalumab": ["astrazeneca"],
    "atezolizumab": ["roche", "genentech"],
    "daratumumab": ["johnson & johnson", "janssen"],
    "secukinumab": ["novartis"],
    "denosumab": ["amgen"],
    "semaglutide": ["novo nordisk"],
    "tirzepatide": ["eli lilly", "lilly"],
    "dulaglutide": ["eli lilly", "lilly"],
    "empagliflozin": ["boehringer", "eli lilly"],
    "dapagliflozin": ["astrazeneca"],
    "canagliflozin": ["johnson & johnson", "janssen"],
    "sitagliptin": ["msd", "merck"],
    "vildagliptin": ["novartis"],
    "linagliptin": ["boehringer"],
    "sacubitril": ["novartis"],
    "osimertinib": ["astrazeneca"],
    "olaparib": ["astrazeneca"],
    "palbociclib": ["pfizer"],
    "ribociclib": ["novartis"],
    "abemaciclib": ["eli lilly", "lilly"],
    "ibrutinib": ["johnson & johnson", "janssen", "pharmacyclics"],
    "acalabrutinib": ["astrazeneca"],
    "ruxolitinib": ["novartis", "incyte"],
    "tofacitinib": ["pfizer"],
    "baricitinib": ["eli lilly", "lilly"],
    "upadacitinib": ["abbvie"],
    "aflibercept": ["bayer", "regeneron"],
    "ranibizumab": ["novartis", "genentech"],
    "brolucizumab": ["novartis"],
    "faricimab": ["roche"],
    "pegfilgrastim": ["amgen"],
    "filgrastim": ["amgen"],
    "epoetin": ["amgen", "johnson & johnson"],
    "darbepoetin": ["amgen"],
    "somatropin": ["novo nordisk", "pfizer", "sandoz"],
    "teriparatide": ["eli lilly", "lilly"],
    "insulin glargine": ["sanofi"],
    "insulin aspart": ["novo nordisk"],
    "insulin lispro": ["eli lilly", "lilly"],
    "insulin degludec": ["novo nordisk"]
}

# Biologic suffixes & patterns
BIOLOGIC_PATTERNS = [
    r'\bmab\b', r'mab\b', r'\bcept\b', r'cept\b', r'\bkin\b', r'\bstim\b',
    r'interferon', r'interleukin', r'insulin', r'somatropin', r'vaccine',
    r'erythropoietin', r'darbepoetin', r'pegfilgrastim', r'filgrastim',
    r'immunoglobulin', r'botulinum', r'factor viii', r'factor ix',
    r'alteplase', r'tenecteplase', r'streptokinase', r'urokinase',
    r'hyaluronidase', r'asparaginase', r'pancreatin', r'teriparatide'
]

def clean_drug_molecule(name):
    if not name:
        return ""
    # Strip dosage forms and strengths
    s = name
    s = re.sub(r'\(.*?\)', '', s)
    s = re.sub(r'\b(drug substance|drug product|bulk drug|bulk|formulated drug|substance|formulated)\b.*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\b(tablet|capsule|injection|infusion|solution|suspension|powder|cream|gel|ointment|drops|syrup|inhalation|extended release|prolonged release|sustained release|dispersible|mouth dissolving|ip|usp|bp|ih|dry syrup|concentrate|lyophilized|for injection)\b.*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\b\d+(\.\d+)?\s*(mg|mcg|gm|g|ml|iu|u|%|w/v|w/w)\b.*', '', s, flags=re.IGNORECASE)
    s = s.strip(" ,.-+/")
    # Take first molecule if combination (+)
    parts = re.split(r'\s*\+\s*|\s+and\s+', s, flags=re.IGNORECASE)
    return parts[0].strip().title()

def standardize_company(comp):
    try:
        from data_pipeline.standardize_companies import standardize_company_name
        return standardize_company_name(comp)
    except ImportError:
        try:
            from standardize_companies import standardize_company_name
            return standardize_company_name(comp)
        except ImportError:
            return comp.strip() if comp else "Unknown"

def is_biologic(drug_name, composition, category):
    text = (drug_name + " " + composition).lower()
    if any(re.search(pat, text) for pat in BIOLOGIC_PATTERNS):
        return True
    return False

def clean_brand_name(raw_pct, drug_name):
    if not raw_pct:
        return None
    raw_pct = raw_pct.strip()
    lower = raw_pct.lower()
    if lower in ['na', 'n/a', 'not applicable', 'nil', 'none', '']:
        return None
    # If pct just repeats full generic formulation name, skip
    if lower == drug_name.lower().strip():
        return None
    return raw_pct

def run_enrichment():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. Add new columns if not already existing
    c.execute("PRAGMA table_info(approvals)")
    existing_cols = [r[1] for r in c.fetchall()]

    new_cols = [
        ("brand_name", "TEXT"),
        ("clean_molecule", "TEXT"),
        ("company_std", "TEXT"),
        ("molecule_type", "TEXT"),
        ("regulatory_type", "TEXT")
    ]

    for col_name, col_type in new_cols:
        if col_name not in existing_cols:
            print(f"Adding column {col_name}...")
            c.execute(f"ALTER TABLE approvals ADD COLUMN {col_name} {col_type}")

    conn.commit()

    # 2. Fetch all approvals ordered by approval_date
    c.execute("SELECT id, drug_name, company, composition, applied_for, approval_date, approval_year, raw_json FROM approvals ORDER BY id ASC")
    rows = c.fetchall()
    print(f"Total rows to enrich: {len(rows)}")

    # First pass: compute earliest approval date and company per molecule in database
    molecule_first_record = {}
    parsed_rows = []

    for r in rows:
        d_name = r["drug_name"] or ""
        comp = r["company"] or ""
        compo = r["composition"] or ""
        app_date = r["approval_date"] or ""
        app_year = r["approval_year"] or 0
        raw = json.loads(r["raw_json"]) if r["raw_json"] else {}
        pct = raw.get("str_pct_name", "")

        brand = clean_brand_name(pct, d_name)
        mol = clean_drug_molecule(d_name)
        comp_std = standardize_company(comp)
        biologic = is_biologic(d_name, compo, r["applied_for"])
        mol_type = "Biologic" if biologic else "Small Molecule"

        mol_lower = mol.lower()
        if mol_lower and mol_lower not in molecule_first_record:
            molecule_first_record[mol_lower] = {
                "first_date": app_date,
                "first_year": app_year,
                "first_company_std": comp_std,
                "first_company_raw": comp
            }

        parsed_rows.append({
            "id": r["id"],
            "brand": brand,
            "mol": mol,
            "mol_lower": mol_lower,
            "comp_std": comp_std,
            "comp_raw": comp,
            "mol_type": mol_type,
            "app_date": app_date,
            "app_year": app_year
        })

    # Second pass: Determine regulatory_type (Innovator vs Biosimilar vs Generic)
    updates = []
    innovator_count = 0
    biosimilar_count = 0
    generic_count = 0

    for item in parsed_rows:
        mol_lower = item["mol_lower"]
        comp_raw_lower = item["comp_raw"].lower()
        comp_std_lower = item["comp_std"].lower()
        mol_type = item["mol_type"]
        brand_lower = (item["brand"] or "").lower()

        is_innovator = False

        # Direct check for known innovator brand names
        if "enhertu" in brand_lower:
            is_innovator = True

        # 1. Check known global innovator database (longest molecule name first)
        if not is_innovator:
            matched_known_mol = None
            for known_m in sorted(KNOWN_INNOVATORS.keys(), key=len, reverse=True):
                if known_m == mol_lower or known_m in mol_lower:
                    matched_known_mol = known_m
                    break

            if matched_known_mol:
                if any(inv in comp_raw_lower for inv in KNOWN_INNOVATORS[matched_known_mol]):
                    is_innovator = True
                else:
                    is_innovator = False
            else:
                # 2. Check if this company is the first chronological originator in India for this molecule
                first_info = molecule_first_record.get(mol_lower)
                if first_info and item["comp_std"] == first_info["first_company_std"]:
                    is_innovator = True

        if is_innovator:
            reg_type = "Innovator"
            innovator_count += 1
        elif mol_type == "Biologic":
            reg_type = "Biosimilar"
            biosimilar_count += 1
        else:
            reg_type = "Generic"
            generic_count += 1

        updates.append((item["brand"], item["mol"], item["comp_std"], item["mol_type"], reg_type, item["id"]))

    # Bulk update
    print("Writing enriched updates to database...")
    c.executemany("""
        UPDATE approvals 
        SET brand_name = ?, clean_molecule = ?, company_std = ?, molecule_type = ?, regulatory_type = ?
        WHERE id = ?
    """, updates)

    # Create indexes for fast filtering
    c.execute("CREATE INDEX IF NOT EXISTS idx_approvals_comp_std ON approvals(company_std)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_approvals_clean_mol ON approvals(clean_molecule)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_approvals_reg_type ON approvals(regulatory_type)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_approvals_mol_type ON approvals(molecule_type)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_approvals_app_date ON approvals(approval_date)")

    conn.commit()
    conn.close()

    print(f"Enrichment Complete!")
    print(f"Innovators: {innovator_count}")
    print(f"Biosimilars: {biosimilar_count}")
    print(f"Generics: {generic_count}")

if __name__ == "__main__":
    run_enrichment()
