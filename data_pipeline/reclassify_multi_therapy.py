"""
CDSCO MULTI-LABEL THERAPY AREA CLASSIFIER & DATABASE MIGRATION
Diligent classification combining active molecule pharmacology and clinical indication text.
"""
import sqlite3
import re
import os

DB_PATH = "cdsco_approvals.db"

# Clinical Indication Regex Dictionaries for Therapeutic Specialties
CLINICAL_INDICATION_MAP = {
    "Oncology": [
        r'\bcancer\b', r'\bcarcinoma\b', r'\btumou?r(s)?\b', r'\blymphoma\b', r'\bleuka?emia\b',
        r'\bmyeloma\b', r'\bneoplasm\b', r'\bmelanoma\b', r'\bsarcoma\b', r'\bglioma\b',
        r'\bglioblastoma\b', r'\bnsclc\b', r'\bsclc\b', r'\bher2\b', r'\boncology\b',
        r'\bmalignan', r'\bantineoplastic\b', r'\bchemotherapy\b', r'\bmetastatic\b',
        r'\bhcc\b', r'\bmcrc\b', r'\bmrcc\b', r'\bsolid\s+tumou?rs\b', r'\bcolorectal\b',
        r'\bcholangiocarcinoma\b', r'\bprostate\s+cancer\b', r'\bbreast\s+cancer\b',
        r'\blung\s+cancer\b', r'\bovarian\b', r'\bcervical\s+cancer\b', r'\bgastric\s+cancer\b'
    ],
    "Rheumatology": [
        r'\brheumatoid\s+arthritis\b', r'\bpsoriatic\s+arthritis\b', r'\bankylosing\s+spondylitis\b',
        r'\baxial\s+spondyloarthritis\b', r'\bspondyloarthritis\b', r'\bjuvenile\s+idiopathic\s+arthritis\b',
        r'\bpolyangiitis\b', r'\bwegener\b', r'\blupus\b', r'\bsystemic\s+lupus\b', r'\bsle\b',
        r'\bgout\b', r'\bhyperuricemia\b', r'\bjia\b', r'\bgiant\s+cell\s+arteritis\b',
        r'\bvasculitis\b', r'\bscleroderma\b', r'\bsj[oö]gren\b', r'\bosteoarthritis\b'
    ],
    "Dermatology": [
        r'\bplaque\s+psoriasis\b', r'\bpsoriasis\b', r'\batopic\s+dermatitis\b', r'\bdermatitis\b',
        r'\beczema\b', r'\bhidradenitis\s+suppurativa\b', r'\bacne\b', r'\bacne\s+inversa\b',
        r'\balopecia(\s+areata)?\b', r'\bvitiligo\b', r'\bcutaneous\b', r'\bprurigo\s+nodularis\b',
        r'\bpemphigus\s+vulgaris\b', r'\burticaria\b', r'\bpruritus\b', r'\bskin\s+infections?\b',
        r'\btinea\b', r'\bonychomycosis\b', r'\bscabies\b', r'\berosive\s+dermatosis\b'
    ],
    "Gastroenterology": [
        r'\bulcerative\s+colitis\b', r'\bcrohn(?:\'s)?(\s+disease)?\b', r'\bibd\b',
        r'\binflammatory\s+bowel\b', r'\bgerd\b', r'\bgastro[a-z]*', r'\bcolitis\b',
        r'\besophagitis\b', r'\bgastric\s+ulcer\b', r'\bduodenal\s+ulcer\b', r'\bpeptic\s+ulcer\b',
        r'\bcirrhosis\b', r'\bhepatic\s+encephalopathy\b', r'\bhepatitis\b', r'\bcholangitis\b',
        r'\bconstipation\b', r'\bdiarrh?oea\b', r'\beosinophilic\s+esophagitis\b',
        r'\bbowel\s+cleansing\b', r'\bh\.?\s*pylori\b', r'\bacid\s+peptic\b', r'\bnash\b', r'\bmash\b'
    ],
    "Cardiology": [
        r'\bhypertension\b', r'\bblood\s+pressure\b', r'\bcardiovascular\b', r'\bheart\s+failure\b',
        r'\bangina\b', r'\bmyocardial\s+infarction\b', r'\barrhythmia\b', r'\batherosclerosis\b',
        r'\bantihypertensive\b', r'\bstroke\b', r'\bcardiac\b', r'\bthrombosis\b', r'\bthromboembolism\b',
        r'\bdvt\b', r'\bpulmonary\s+embolism\b', r'\bcholesterol\b', r'\bdyslipidemia\b',
        r'\bhypercholesterolemia\b', r'\batrial\s+fibrillation\b', r'\bacute\s+coronary\b',
        r'\bpulmonary\s+arterial\s+hypertension\b', r'\bhfref\b', r'\bhfpef\b', r'\bcoronary\s+artery\b'
    ],
    "Diabetology": [
        r'\btype\s*2\s*diabetes\b', r'\btype\s*1\s*diabetes\b', r'\bt2dm\b', r'\bt1dm\b',
        r'\bdiabetes\s+mellitus\b', r'\bdiabetic\b', r'\bglyca?emic\b', r'\bhba1c\b',
        r'\bhypoglyca?emia\b', r'\bhyperglyca?emia\b', r'\bglucose\s+control\b'
    ],
    "Endocrinology": [
        r'\bobesity\b', r'\bweight\s+management\b', r'\bchronic\s+weight\b', r'\bhypothyroidism\b',
        r'\bhyperthyroidism\b', r'\bthyroid\b', r'\bacromegaly\b', r'\bcushing\b',
        r'\bgrowth\s+hormone\b', r'\bhypoparathyroidism\b', r'\bosteoporosis\b'
    ],
    "Pulmonology": [
        r'\basthma\b', r'\bcopd\b', r'\bbronchitis\b', r'\brespiratory\b', r'\bpulmonary\s+fibrosis\b',
        r'\bipf\b', r'\bbronchospasm\b', r'\bcystic\s+fibrosis\b', r'\binhalation\b',
        r'\bbronchodilat\b', r'\bcough\b'
    ],
    "Neurology": [
        r'\bepilepsy\b', r'\bseizure(s)?\b', r'\bparkinson(?:\'s)?\b', r'\balzheimer(?:\'s)?\b',
        r'\bmigraine\b', r'\bneuropathic\s+pain\b', r'\bneuropathy\b', r'\bconvulsion\b',
        r'\bmultiple\s+sclerosis\b', r'\bdementia\b', r'\bspasticity\b', r'\bspinal\s+muscular\s+atrophy\b',
        r'\bsma\b', r'\bamyotrophic\s+lateral\s+sclerosis\b', r'\bmyasthenia\s+gravis\b',
        r'\btardive\s+dyskinesia\b', r'\bchorea\b', r'\bcns\b'
    ],
    "Psychiatry": [
        r'\bschizophrenia\b', r'\bdepression\b', r'\bdepressive\b', r'\bmajor\s+depressive\b',
        r'\bmdd\b', r'\banxiety\b', r'\binsomnia\b', r'\bbipolar\b', r'\bpsychosis\b',
        r'\bantidepressant\b', r'\bantipsychotic\b', r'\badhd\b', r'\bpanic\s+disorder\b'
    ],
    "Ophthalmology": [
        r'\bophthalmic\b', r'\bocular\b', r'\beye\b', r'\bglaucoma\b', r'\bmacular\s+edema\b',
        r'\bmacular\s+degeneration\b', r'\bamd\b', r'\bconjunctivitis\b', r'\bretinopathy\b',
        r'\bdiabetic\s+retinopathy\b', r'\bdiabetic\s+macular\b', r'\buveitis\b', r'\bcataract\b',
        r'\bintraocular\b', r'\bcorneal\b'
    ],
    "Nephrology": [
        r'\bchronic\s+kidney\s+disease\b', r'\bckd\b', r'\brenal\s+impairment\b', r'\bkidney\s+disease\b',
        r'\bdialysis\b', r'\bhyperkalemia\b', r'\bhyperphosphatemia\b', r'\blupus\s+nephritis\b',
        r'\biga\s+nephropathy\b', r'\bnephrotic\b', r'\bkidney\s+transplant\b'
    ],
    "Anti-Infectives": [
        r'\bbacterial\s+infections?\b', r'\bantibiotic\b', r'\bantimicrobial\b', r'\bantiviral\b',
        r'\bfungal\s+infections?\b', r'\bantifungal\b', r'\bhiv\b', r'\btuberculosis\b',
        r'\bmalaria\b', r'\bsepsis\b', r'\bpneumonia\b', r'\bantiprotozoal\b', r'\bcovid\b',
        r'\bherpes\b', r'\bparasitic\b', r'\bmeningitis\b'
    ],
    "Immunology & Allergy": [
        r'\ballergic\s+rhinitis\b', r'\ballergy\b', r'\ballergic\b', r'\bantihistamine\b',
        r'\banaphylaxis\b', r'\bangioedema\b', r'\bhereditary\s+angioedema\b'
    ],
    "Urology": [
        r'\bbenign\s+prostatic\b', r'\bbph\b', r'\bmicturition\b', r'\bbladder\b',
        r'\burinary\s+incontinence\b', r'\boveractive\s+bladder\b', r'\berectile\s+dysfunction\b',
        r'\bprostatic\s+hyperplasia\b'
    ],
    "Women's Health": [
        r'\bcontracepti\b', r'\bpregnancy\b', r'\bmenopause\b', r'\binfertility\b',
        r'\bendometriosis\b', r'\buterine\s+fibroids\b', r'\bpostpartum\s+haemorrhage\b',
        r'\bpostpartum\s+hemorrhage\b', r'\bheavy\s+menstrual\b', r'\bovulation\s+induction\b'
    ],
    "Hematology": [
        r'\bha?emophilia\b', r'\bcoagulation\s+factor\b', r'\bfactor\s+viii\b', r'\bfactor\s+ix\b',
        r'\bthrombocytopenia\b', r'\bitp\b', r'\bsickle\s+cell\b', r'\bthalassa?emia\b',
        r'\bana?emia\b', r'\bparoxysmal\s+nocturnal\b', r'\bpnh\b'
    ],
    "Pain & Analgesics": [
        r'\bacute\s+pain\b', r'\bchronic\s+pain\b', r'\bpostoperative\s+pain\b', r'\banalgesic\b',
        r'\bmusculoskeletal\s+pain\b', r'\bfever\b', r'\bpyretic\b'
    ],
    "Anesthesia & Critical Care": [
        r'\bana?esthesia\b', r'\bana?esthetic\b', r'\bsedation\b', r'\bneuromuscular\s+block\b',
        r'\bvasodilatory\s+shock\b'
    ],
    "Rare Diseases & ERT": [
        r'\brare\s+disease\b', r'\bhunter\s+syndrome\b', r'\bgaucher\b', r'\bfabry\b',
        r'\bmucopolysaccharidosis\b', r'\btyrosinemia\b', r'\bcystinosis\b', r'\benzyme\s+replacement\b'
    ],
    "Vaccines": [
        r'\bvaccine\b', r'\btoxoid\b', r'\bimmuni[sz]ation\b', r'\bactive\s+immuni[sz]ation\b',
        r'\bprophylaxis\s+of\s+(tetanus|diphtheria|rabies|measles|influenza|polio|covid)\b'
    ]
}

# Special multi-specialty canonical molecule definitions
MULTI_SPECIALTY_MOLECULES = {
    "secukinumab": ["Rheumatology", "Dermatology"],
    "guselkumab": ["Gastroenterology", "Dermatology", "Rheumatology"],
    "ixekizumab": ["Dermatology", "Rheumatology"],
    "bimekizumab": ["Dermatology", "Rheumatology"],
    "ustekinumab": ["Gastroenterology", "Dermatology", "Rheumatology"],
    "risankizumab": ["Gastroenterology", "Dermatology", "Rheumatology"],
    "dupilumab": ["Dermatology", "Pulmonology", "Gastroenterology"],
    "upadacitinib": ["Rheumatology", "Dermatology", "Gastroenterology"],
    "tofacitinib": ["Rheumatology", "Dermatology", "Gastroenterology"],
    "baricitinib": ["Rheumatology", "Dermatology"],
    "adalimumab": ["Rheumatology", "Dermatology", "Gastroenterology", "Ophthalmology"],
    "infliximab": ["Rheumatology", "Gastroenterology", "Dermatology"],
    "rituximab": ["Oncology", "Rheumatology", "Dermatology"],
    "methotrexate": ["Oncology", "Rheumatology", "Dermatology"],
    "apremilast": ["Dermatology", "Rheumatology"],
    "semaglutide": ["Diabetology", "Endocrinology", "Cardiology"],
    "tirzepatide": ["Diabetology", "Endocrinology"],
    "dapagliflozin": ["Diabetology", "Cardiology", "Nephrology"],
    "empagliflozin": ["Diabetology", "Cardiology", "Nephrology"]
}

def clean_indication_text(ind_text):
    if not ind_text:
        return ""
    text = ind_text.lower()
    # Strip clinical trial section references: "see section 5.1", "see section 4.4"
    text = re.sub(r'see\s+section\s*[\d\.]+', ' ', text)
    # Strip study results cross-references
    text = re.sub(r'for\s+study\s+results\s+with\s+respect\s+to[^\.,;]*[,\.]', ' ', text)
    # Strip organ impairment warnings: "in patients with hepatic impairment"
    text = re.sub(r'in\s+patients\s+with\s+(renal|hepatic|hepatic\s+or\s+renal)\s+impairment', ' ', text)
    # Strip dose adjustments
    text = re.sub(r'(renal|hepatic)\s+dose\s+adjustment', ' ', text)
    return text

def classify_multi_therapy(drug_name, clean_mol, indication, composition, current_ta):
    cleaned_ind = clean_indication_text(indication)
    mol_text = (clean_mol or drug_name or "").lower()
    
    matched_tas = []
    
    # 1. Match from cleaned indication text
    if cleaned_ind and cleaned_ind != "na" and len(cleaned_ind) > 4:
        for ta, patterns in CLINICAL_INDICATION_MAP.items():
            for pat in patterns:
                if re.search(pat, cleaned_ind):
                    # Precision guards
                    if ta == "Dermatology" and "psoriatic arthritis" in cleaned_ind:
                        non_psa_skin = re.search(r'\b(plaque\s+psoriasis|dermatitis|eczema|hidradenitis|acne|alopecia|prurigo|vitiligo|rash|skin)\b', cleaned_ind)
                        if not non_psa_skin:
                            continue
                            
                    if ta == "Urology" and ("prostate cancer" in cleaned_ind or "psma" in cleaned_ind or "carcinoma" in cleaned_ind):
                        if not re.search(r'\b(bph|benign\s+prostatic|micturition|incontinence|overactive\s+bladder|erectile)\b', cleaned_ind):
                            continue
                            
                    if ta == "Diabetology" and ("diabetic retinopathy" in cleaned_ind or "diabetic macular" in cleaned_ind):
                        if not re.search(r'\b(type\s*2|type\s*1|t2dm|t1dm|glucose\s+control|glyca?emic|hba1c)\b', cleaned_ind):
                            continue

                    if ta == "Pulmonology" and "pulmonary arterial hypertension" in cleaned_ind:
                        if not re.search(r'\b(asthma|copd|bronchitis|fibrosis|cough|respiratory\s+tract)\b', cleaned_ind):
                            continue

                    matched_tas.append(ta)
                    break

    # If indication matched 1 or more areas, return them
    if matched_tas:
        return ", ".join(matched_tas)

    # 2. Check canonical multi-specialty molecules if indication was uninformative/NA
    for m_key, m_tas in MULTI_SPECIALTY_MOLECULES.items():
        if m_key in mol_text:
            return ", ".join(m_tas)

    # 3. Fallback: preserve existing valid therapy area if not 'Other' / 'Excipients'
    if current_ta and current_ta not in ["Other", "Excipients & Solvents"]:
        return current_ta

    return "Other"

def run_migration():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, drug_name, clean_molecule, therapy_area, indication, composition FROM approvals ORDER BY id ASC")
    rows = c.fetchall()
    print(f"Total rows to evaluate: {len(rows)}")

    updated_count = 0
    multi_tag_count = 0
    
    for r in rows:
        rid, dname, cmol, old_ta, ind, comp = r
        new_ta = classify_multi_therapy(dname, cmol, ind, comp, old_ta)
        
        if new_ta != old_ta:
            c.execute("UPDATE approvals SET therapy_area = ? WHERE id = ?", (new_ta, rid))
            updated_count += 1
            
        if "," in new_ta:
            multi_tag_count += 1

    conn.commit()
    print(f"\nMigration complete!")
    print(f"  Rows updated: {updated_count}")
    print(f"  Rows with multiple therapy area tags: {multi_tag_count} / {len(rows)} ({multi_tag_count/len(rows)*100:.1f}%)")

    # Verification on Secukinumab
    print("\n--- SECUKINUMAB AUDIT ---")
    c.execute("SELECT id, drug_name, therapy_area, indication FROM approvals WHERE clean_molecule LIKE '%Secukinumab%' OR drug_name LIKE '%Secukinumab%'")
    for r in c.fetchall():
        print(f"ID {r[0]} | TA: {r[2]}")
        print(f"   Indication: {r[3][:100]}...")

    conn.close()

if __name__ == "__main__":
    run_migration()
