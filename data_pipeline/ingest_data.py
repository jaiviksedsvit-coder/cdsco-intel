import urllib.request
import ssl
import json
import sqlite3
import os
import re

DB_PATH = "cdsco_approvals.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_id INTEGER,
    division_id INTEGER,
    drug_name TEXT NOT NULL,
    company TEXT,
    composition TEXT,
    dosage TEXT,
    indication TEXT,
    approval_date TEXT,
    approval_year INTEGER,
    applied_for TEXT,
    manuf_addr TEXT,
    therapy_area TEXT,
    product_category TEXT,
    raw_json TEXT
)
''')

cursor.execute('CREATE INDEX idx_drug_name ON approvals(drug_name);')
cursor.execute('CREATE INDEX idx_company ON approvals(company);')
cursor.execute('CREATE INDEX idx_therapy_area ON approvals(therapy_area);')
cursor.execute('CREATE INDEX idx_product_category ON approvals(product_category);')
cursor.execute('CREATE INDEX idx_approval_year ON approvals(approval_year);')
cursor.execute('CREATE INDEX idx_approval_date ON approvals(approval_date);')

# Simplified, Industry-Standard Therapy Taxonomy
TAXONOMY_RULES = {
    "Oncology": [
        "cancer", "carcinoma", "tumor", "tumour", "lymphoma", "leukemia", "leukaemia",
        "myeloma", "neoplasm", "metastatic", "melanoma", "sarcoma", "glioma", "her2",
        "nsclc", "sclc", "oncology", "malignan", "antineoplastic", "chemotherapy",
        "trastuzumab", "rituximab", "olaparib", "durvalumab", "pembrolizumab", "lenalidomide",
        "bortezomib", "ibrutinib", "osimertinib", "palbociclib", "ribociclib", "regorafenib",
        "abiraterone", "enzalutamide", "fulvestrant", "anastrozole", "letrozole", "erlotinib",
        "gefitinib", "sorafenib", "sunitinib", "rucaparib", "niraparib", "cabozantinib",
        "axitinib", "alectinib", "lorlatinib", "brigatinib", "dabrafenib", "trametinib",
        "venetoclax", "carfilzomib", "pomalidomide", "thalidomide", "capecitabine", "gemcitabine",
        "paclitaxel", "docetaxel", "cisplatin", "carboplatin", "oxaliplatin", "irinotecan",
        "imatinib", "dasatinib", "nilotinib", "bosutinib", "ponatinib", "remibrutinib",
        "doxorubicin", "epirubicin", "methotrexate", "vincristine", "vinblastine", "etoposide",
        "ruxolitinib", "lenvatinib", "tipiracil", "vorasidenib", "belumosudil", "brentuximab",
        "polatuzumab", "pertuzumab", "nivolumab", "atezolizumab", "avelumab", "cemiplimab"
    ],
    "Cardiology": [
        "hypertension", "blood pressure", "cardiovascular", "heart failure", "angina",
        "myocardial", "arrhythmia", "atherosclerosis", "antihypertensive", "stroke",
        "cardiac", "artery", "thrombosis", "cholesterol", "lipid", "statin", "anticoagulant",
        "sacubitril", "valsartan", "ramipril", "bisoprolol", "sartan", "edoxaban", "rivaroxaban",
        "apixaban", "dabigatran", "ticagrelor", "clopidogrel", "prasugrel", "bempedoic",
        "atorvastatin", "rosuvastatin", "pitavastatin", "fimasartan", "azilsartan", "telmisartan",
        "olmesartan", "losartan", "candesartan", "amlodipine", "cilnidipine", "benidipine",
        "midodrine", "esaxerenone", "ivabradine", "ranolazine", "amiodarone", "vericiguat",
        "aspirin", "mavacamten", "diosmin", "macitentan", "ambrisentan", "bosentan", "selexipag"
    ],
    "Diabetology": [
        "diabetes", "diabetic", "glycemic", "glucose", "insulin", "hba1c", "hypoglycemia",
        "t2dm", "t1dm", "semaglutide", "tirzepatide", "sitagliptin", "linagliptin",
        "vildagliptin", "dapagliflozin", "empagliflozin", "metformin", "glimepiride",
        "teneligliptin", "alogliptin", "canagliflozin", "remogliflozin", "glipizide",
        "pioglitazone", "dulaglutide", "liraglutide", "degudec", "glargine", "aspart", "lispro",
        "imeglimin", "lobeglitazone", "trelagliptin"
    ],
    "Anti-Infectives": [
        "bacterial", "infection", "antibiotic", "antimicrobial", "antiviral", "fungal",
        "antifungal", "hiv", "hepatitis", "tuberculosis", "parasitic", "malaria",
        "sepsis", "covid", "pneumonia", "antiprotozoal", "micafungin", "caspofungin",
        "anidulafungin", "sofosbuvir", "remdesivir", "penicillin", "cephalosporin",
        "ciprofloxacin", "favipiravir", "faviravir", "molnupiravir", "itraconazole",
        "voriconazole", "posaconazole", "colistimethate", "colistin", "pretomanid",
        "bedaquiline", "delamanid", "meropenem", "imipenem", "faropenem", "azithromycin",
        "clarithromycin", "doxycycline", "linezolid", "tedizolid", "dalbavancin",
        "vancomycin", "teicoplanin", "polymyxin", "acyclovir", "valacyclovir", "ganciclovir",
        "fosfomycin", "ertapenem", "biapenem", "isavuconazonium", "nirmatrelvir", "avibactam",
        "ozenoxacin", "rifapentine", "fosravuconazole"
    ],
    "Neurology": [
        "epilepsy", "seizure", "parkinson", "alzheimer", "migraine", "neuropathic",
        "neuropathy", "convulsion", "cns", "dementia", "spasticity", "multiple sclerosis",
        "gabapentin", "pregabalin", "levetiracetam", "brivaracetam", "cenobamate",
        "lacosamide", "perampanel", "eslicarbazepine", "valpro", "lamotrigine", "topiramate",
        "donepezil", "memantine", "rivastigmine", "levodopa", "carbidopa", "pramipexole",
        "ropinirole", "erenumab", "fremanezumab", "rimegepant", "ubrogepant", "sumatriptan",
        "vigabatrin", "pitolisant", "betahistine"
    ],
    "Psychiatry": [
        "schizophrenia", "depression", "depressive", "anxiety", "insomnia", "psychiatric",
        "bipolar", "psychosis", "duloxetine", "sertraline", "olanzapine", "escitalopram",
        "quetiapine", "antidepressant", "antipsychotic", "clozapine", "aripiprazole",
        "brexpiprazole", "cariprazine", "lurasidone", "risperidone", "paliperidone",
        "vortioxetine", "vilazodone", "venlafaxine", "mirtazapine", "bupropion", "fluoxetine",
        "clonazepam", "lorazepam", "alprazolam", "zolpidem", "lemborexant", "pimavanserin",
        "lumateperone"
    ],
    "Dermatology": [
        "psoriasis", "dermatitis", "eczema", "skin", "alopecia", "acne", "topical",
        "emollient", "cutaneous", "pruritus", "dermatological", "tretinoin", "adapalene",
        "tapinarof", "dupilumab", "tofacitinib ointment", "guselkumab", "ixekizumab",
        "secukinumab", "clindamycin phosphate", "minoxidil", "isotretinoin", "benzoyl peroxide",
        "crisaborole", "calcipotriol"
    ],
    "Allergy & Immunology": [
        "bilastine", "fexofenadine", "cetirizine", "levocetirizine", "loratadine", "rupatadine",
        "antihistamine", "allergic", "rhinitis", "urticaria", "anaphylaxis", "montelukast",
        "omalizumab"
    ],
    "Rheumatology": [
        "arthritis", "rheumatoid", "autoimmune", "lupus", "immunosuppressive", "ankylosing",
        "spondylitis", "immunosuppressant", "gout", "uric acid", "febuxostat", "adalimumab",
        "infliximab", "tofacitinib", "baricitinib", "upadacitinib", "apremilast", "leflunomide",
        "azathioprine", "mycophenolate", "tacrolimus", "cyclosporine", "topiroxostat"
    ],
    "Urology": [
        "urology", "prostate", "bph", "micturition", "bladder", "urinary", "incontinence",
        "erectile", "tamsulosin", "mirabegron", "silodosin", "finasteride", "sildenafil",
        "tadalafil", "dutasteride", "solifenacin", "darifenacin", "fesoterodine", "avanafil",
        "methenamine"
    ],
    "Nephrology": [
        "nephrology", "renal", "kidney", "dialysis", "hyperkalemia", "hyperphosphatemia",
        "calcimimetic", "sevelamer", "patiromer", "sodium zirconium", "sucroferric",
        "lanthanum", "cinacalcet"
    ],
    "Women's Health": [
        "progesterone", "estrogen", "contraceptive", "pregnancy", "menopause", "infertility",
        "ovulation", "endometriosis", "dydrogesterone", "mifepristone", "clomiphene", "uterine",
        "obstetric", "relugolix", "elagolix", "dienogest", "levonorgestrel", "ethinylestradiol",
        "tranexamic", "oxytocin", "carbetocin", "misoprostol", "follitropin", "lutropin",
        "chorionic gonadotropin", "hcg"
    ],
    "Gastroenterology": [
        "gastro", "ulcer", "reflux", "gerd", "bowel", "colitis", "crohn", "hepatic",
        "cirrhosis", "liver", "constipation", "diarrhea", "acidity", "proton pump",
        "vonoprazan", "pantoprazole", "rabeprazole", "esomeprazole", "omeprazole",
        "tegoprazan", "zastaprazan", "obeticholic", "ursodeoxycholic", "linaclotide",
        "prucalopride", "mesalamine", "rifaximin", "elobixibat"
    ],
    "Pulmonology": [
        "asthma", "copd", "bronchitis", "respiratory", "pulmonary", "inhalation",
        "bronchospasm", "cough", "allergic rhinitis", "formoterol", "budesonide",
        "fluticasone", "tiotropium", "glycopyrronium", "indacaterol", "revefenacin",
        "ivacaftor", "lumacaftor", "pirfenidone", "nintedanib", "acetylcysteine", "umeclidinium"
    ],
    "Hematology": [
        "hemophilia", "haemophilia", "coagulation factor", "factor viii", "factor ix",
        "antihemophilic", "nonacog", "octocog", "rurioctocog", "turoctocog", "von willebrand",
        "thrombocytopenia", "eltrombopag", "romiplostim", "avatrombopag", "sickle cell",
        "thalassemia", "deferasirox", "deferiprone", "erythropoietin", "darbepoetin"
    ],
    "Ophthalmology": [
        "ophthalmic", "ocular", "eye", "glaucoma", "macular", "conjunctivitis", "retinopathy",
        "cataract", "latanoprost", "travoprost", "bimatoprost", "timolol", "brimonidine",
        "dorzolamide", "aflibercept", "ranibizumab", "faricimab", "cyclosporine eye",
        "lifitegrast", "fluorometholone", "moxifloxacin eye", "prednisolone eye", "netarsudil"
    ],
    "Pain & Analgesics": [
        "pain", "analgesic", "fever", "pyretic", "paracetamol", "ibuprofen", "diclofenac",
        "musculoskeletal", "sprain", "aceclofenac", "polmacoxib", "etoricoxib", "celecoxib",
        "tramadol", "tapentadol", "buprenorphine", "fentanyl", "ketorolac"
    ],
    "Anesthesia & Critical Care": [
        "anesthesia", "anaesthesia", "anesthetic", "sedation", "sedative", "sugammadex",
        "dexmedetomidine", "propofol", "sevoflurane", "isoflurane", "rocuronium", "atracurium",
        "bupivacaine", "ropivacaine", "lignocaine", "lidocaine", "remifentanil", "centhaquine"
    ],
    "Endocrinology": [
        "thyroid", "endocrine", "metabolic syndrome", "obesity", "weight management",
        "growth hormone", "pituitary", "adrenal", "hypothyroidism", "hyperthyroidism",
        "acromegaly", "cushing", "somatropin", "levothyroxine", "teriparatide"
    ],
    "Rare Diseases & ERT": [
        "rare disease", "hunter syndrome", "gaucher", "fabry", "mucopolysaccharidosis",
        "idursulfase", "nitisinone", "eliglustat", "cysteamine", "agalsidase", "imiglucerase",
        "tyrosinemia", "cystinosis", "enzyme replacement"
    ],
    "Vaccines": [
        "vaccine", "toxoid", "immunisation", "immunization", "prophylaxis of influenza",
        "tetanus", "diphtheria", "pertussis", "poliomyelitis", "corona virus", "covid-19",
        "rabies", "hepatitis b vaccine", "measles", "rubella", "antirabies", "antisera",
        "snake venom", "immunoglobulin", "monovalent inactivated", "hib conjugate"
    ],
    "VMS & Nutrition": [
        "vitamin", "cholecalciferol", "calcium carbonate", "calcitriol", "alpha lipoic",
        "amino acid", "leucine", "isoleucine", "valine", "ketoisoleucine", "keto-acid",
        "dextrose", "sodium chloride", "electrolyte", "parenteral nutrition", "zinc acetate",
        "folic acid", "methylcobalamin", "cyanocobalamin", "iron", "ferric", "potassium chloride",
        "levocarnitine", "l-carnitine", "nutrition", "supplement"
    ],
    "Diagnostics & Imaging": [
        "contrast", "radiopaque", "iodixanol", "iohexol", "iopamidol", "gadobutrol",
        "gadoterate", "gadolinium", "barium", "diagnostic agent", "technetium"
    ],
    "Excipients & Solvents": [
        "water for injection", "sodium hydroxide", "glacial acetic acid", "phosphate buffered saline",
        "glycine", "sorbitol", "glycerol", "citric acid", "sucrose", "l-histidine", "mannitol",
        "polysorbate", "nicotine transdermal"
    ]
}

def classify(drug_name, indication, composition):
    from reclassify_multi_therapy import classify_multi_therapy
    return classify_multi_therapy(drug_name, "", indication, composition, "")

def get_product_category(applied_for, drug_name):
    txt = f"{applied_for} {drug_name}".lower()
    if "bulk" in txt:
        return "Bulk API"
    return "Finished Formulation"

def extract_year(date_str, default_year):
    if not date_str:
        return default_year
    m = re.search(r'(\d{4})', str(date_str))
    if m:
        return int(m.group(1))
    m2 = re.search(r'(\d{2})$', str(date_str).strip())
    if m2:
        yr = int(m2.group(1))
        return 2000 + yr if yr <= 30 else 1900 + yr
    return default_year

# Ingestion loop
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://cdscoonline.gov.in/CDSCO/cdscoDrugs'}

years = ['2026', '2025', '2024', '2023', '2022', '2021', '2020', '2019', '2018']
total_inserted = 0

print("Rebuilding database with simplified, clean therapy taxonomy...")

for y in years:
    try:
        url = f"https://cdscoonline.gov.in/CDSCO/loadDrugApprovals?searchText=&year={y}&month=&drugTypeValue="
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            raw = r.read().decode('utf-8', errors='ignore')
            data = json.loads(raw)
            items = data.get('aaData', [])
            
            for item in items:
                drug_name = (item.get('str_drug_name') or '').strip()
                company = (item.get('str_man_unit_name') or '').strip()
                composition = (item.get('str_composition') or '').strip()
                dosage = (item.get('str_dosage') or '').strip()
                indication = (item.get('str_indication') or '').strip()
                dt_str = (item.get('dt_closure_dt') or '').strip()
                form_id = item.get('num_form_id')
                div_id = item.get('num_division_id')
                applied_for = (item.get('str_applied_for') or '').strip()
                manuf_addr = (item.get('manuf_addr') or '').strip()
                
                yr_val = extract_year(dt_str, int(y))
                ta = classify(drug_name, indication, composition)
                cat = get_product_category(applied_for, drug_name)
                
                cursor.execute('''
                INSERT INTO approvals (
                    form_id, division_id, drug_name, company, composition, dosage,
                    indication, approval_date, approval_year, applied_for, manuf_addr,
                    therapy_area, product_category, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    form_id, div_id, drug_name, company, composition, dosage,
                    indication, dt_str, yr_val, applied_for, manuf_addr,
                    ta, cat, json.dumps(item)
                ))
                total_inserted += 1
                
        conn.commit()
    except Exception as e:
        print(f"Error for year {y}: {e}")

conn.commit()

# Final report
cursor.execute("SELECT COUNT(*) FROM approvals")
total = cursor.fetchone()[0]

cursor.execute("SELECT therapy_area, COUNT(*) FROM approvals GROUP BY therapy_area ORDER BY COUNT(*) DESC")
stats = cursor.fetchall()

print(f"\n==========================================")
print(f"  SIMPLIFIED TAXONOMY REPORT ({total} RECORDS)")
print(f"==========================================")
for ta, count in stats:
    pct = (count / total) * 100
    print(f"{ta:<28} | {count:>5} records | {pct:>5.1f}%")

cursor.execute("SELECT product_category, COUNT(*) FROM approvals GROUP BY product_category")
pcat_stats = cursor.fetchall()
print("\nPRODUCT CATEGORIES:")
for pcat, count in pcat_stats:
    pct = (count / total) * 100
    print(f"  - {pcat}: {count} ({pct:.1f}%)")

conn.close()
