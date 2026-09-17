"""
Standardize Company Names across CDSCO Approvals Database.
Eliminates repeating prefixes (e.g. M/s, M/S), unifies subsidiaries/divisions
(e.g. MSN Laboratories, Shilpa Medicare, BDR Pharmaceuticals, Optimus Pharma),
and corrects false substring matches (e.g. Metrochem mapped to Roche).
"""

import sqlite3
import re
from collections import Counter

DB_PATH = "cdsco_approvals.db"

# Canonical Company Standardization Rules
# List of (regex_pattern, canonical_name)
# Evaluated in strict order with word boundaries
COMPANY_RULES = [
    # 1. False substring match guards first!
    (r'\bmetrochem\b', "Metrochem API"),

    # 2. MSN Group (Resolves user specific example: M/S MSN and MSN)
    (r'\bmsn\b', "MSN Laboratories"),

    # 3. Top MNCs (Use word boundaries to prevent false substring matches)
    (r'\bastrazeneca\b', "AstraZeneca"),
    (r'\broche\b|\bgenentech\b|\bchugai\b', "Roche"),
    (r'\bnovartis\b|\bsandoz\b', "Novartis"),
    (r'\bpfizer\b|\bupjohn\b', "Pfizer"),
    (r'\bsanofi\b|\baventis\b', "Sanofi"),
    (r'\bmsd\b|\bmerck sharp\b', "MSD Pharma"),
    (r'\bmerck (specialities|healthcare|life science|development center)\b', "Merck Group"),
    (r'\bjohnson & johnson\b|\bjanssen\b|\bcilag\b', "Johnson & Johnson"),
    (r'\beli lilly\b|\blilly\b', "Eli Lilly"),
    (r'\babbott\b', "Abbott"),
    (r'\babbvie\b', "AbbVie"),
    (r'\bbayer\b', "Bayer"),
    (r'\bboehringer\b', "Boehringer Ingelheim"),
    (r'\bnovo nordisk\b', "Novo Nordisk"),
    (r'\btakeda\b', "Takeda"),
    (r'\bamgen\b', "Amgen"),
    (r'\bbristol[- ]myers\b|\bbms\b', "Bristol Myers Squibb"),
    (r'\bgilead\b', "Gilead Sciences"),
    (r'\bferring\b', "Ferring Pharmaceuticals"),
    (r'\bastellas\b', "Astellas Pharma"),
    (r'\bdaiichi\b', "Daiichi Sankyo"),
    (r'\botsuka\b', "Otsuka Pharmaceutical"),
    (r'\bgsk\b|\bglaxosmithkline\b|\bglaxo\b', "GlaxoSmithKline"),
    (r'\bservier\b', "Servier"),
    (r'\bteva\b', "Teva Pharmaceuticals"),
    (r'\beisei\b|\beisai\b', "Eisai"),
    (r'\balcon\b', "Alcon"),
    (r'\ballergan\b', "Allergan"),
    (r'\bkyowa\b', "Kyowa Kirin"),
    (r'\bmerck\b', "Merck Group"),

    # 4. Top Indian Pharma Majors & Groups
    (r'\bdr\.?\s*reddy\b', "Dr. Reddy's Laboratories"),
    (r'\bsun pharma\b|\bsun pharmaceutical\b', "Sun Pharma"),
    (r'\bcipla\b', "Cipla"),
    (r'\bzydus\b|\bcadila healthcare\b', "Zydus Lifesciences"),
    (r'\blupin\b', "Lupin"),
    (r'\bmankind\b', "Mankind Pharma"),
    (r'\bhetero\b', "Hetero Labs"),
    (r'\btorrent\b', "Torrent Pharma"),
    (r'\bintas\b', "Intas Pharmaceuticals"),
    (r'\balkem\b', "Alkem Laboratories"),
    (r'\bbiocon\b', "Biocon"),
    (r'\bnatco\b', "Natco Pharma"),
    (r'\bglenmark\b', "Glenmark Pharmaceuticals"),
    (r'\beris\b', "Eris Lifesciences"),
    (r'\bmylan\b|\bviatris\b', "Viatris / Mylan"),
    (r'\bajanta\b', "Ajanta Pharma"),
    (r'\balembic\b', "Alembic Pharmaceuticals"),
    (r'\bipca\b', "Ipca Laboratories"),
    (r'\bmicro labs\b', "Micro Labs"),
    (r'\bemcure\b', "Emcure Pharmaceuticals"),
    (r'\bwockhardt\b', "Wockhardt"),
    (r'\bpanacea\b', "Panacea Biotec"),
    (r'\bserum institute\b', "Serum Institute of India"),
    (r'\bbharat biotech\b', "Bharat Biotech"),
    (r'\bbharat serums\b', "Bharat Serums And Vaccines"),
    (r'\bbharat parenterals\b', "Bharat Parenterals"),
    (r'\bbiological e\b|\bbiological e\.\b', "Biological E"),
    (r'\bwindlas\b', "Windlas Biotech"),
    (r'\bpure & cure\b', "Pure & Cure Healthcare"),
    (r'\bakums\b', "Akums Drugs & Pharmaceuticals"),
    (r'\bmacleods\b', "Macleods Pharmaceuticals"),
    (r'\baristo\b', "Aristo Pharmaceuticals"),
    (r'\busv\b', "USV Private Limited"),
    (r'\bindoco\b', "Indoco Remedies"),
    (r'\bsuven\b', "Suven Pharmaceuticals"),
    (r'\blaurus\b', "Laurus Labs"),
    (r'\bgland\b', "Gland Pharma"),
    (r'\btroikaa\b', "Troikaa Pharmaceuticals"),
    (r'\bpiramal\b|\bnicholas piramal\b', "Piramal Healthcare"),
    (r'\bj\.?\s*b\.?\s*chemicals\b|\bunique pharmaceutical\b', "J.B. Chemicals & Pharmaceuticals"),
    (r'\bshilpa\b', "Shilpa Medicare"),
    (r'\bbdr\b', "BDR Pharmaceuticals"),
    (r'\boptimus\b', "Optimus Pharma"),
    (r'\btheon\b', "Theon Pharmaceuticals"),
    (r'\blee pharma\b|\blee\b', "Lee Pharma"),
    (r'\bmaithri\b', "Maithri Drugs"),
    (r'\bbeta drugs\b', "Beta Drugs"),
    (r'\bbiogenomics\b', "BioGenomics"),
    (r'\bacme\b', "Acme Generics"),
    (r'\baurore\b', "Aurore Life Sciences"),
    (r'\bswiss garnier\b', "Swiss Garnier"),
    (r'\bsymbio\b', "Symbio Generics"),
    (r'\bm\.?\s*j\.?\s*biopharm\b', "M.J. Biopharm"),
    (r'\bcenturion\b', "Centurion Remedies"),
    (r'\boneiro\b', "Oneiro Lifecare"),
    (r'\brakshit\b', "Rakshit Drugs"),
    (r'\bkreative\b', "Kreative Organics"),
    (r'\bstrides\b', "Strides Pharma"),
    (r'\binnova captab\b', "Innova Captab"),
    (r'\bravenbhel\b', "Ravenbhel Healthcare"),
    (r'\bsignature phytochemical\b', "Signature Phytochemical"),
    (r'\bfourts\b', "Fourts India Laboratories"),
    (r'\balmelo\b', "Almelo Private Limited"),
    (r'\btenshi\b', "Tenshi Kaizen"),
    (r'\bscott edil\b', "Scott Edil Pharmacia"),
    (r'\bcelebrity biopharma\b', "Celebrity Biopharma"),
    (r'\bgcbc vaccines\b', "GCBC Vaccines"),
    (r'\bsionc\b', "Sionc Pharmaceuticals"),
    (r'\bvxl life sciences\b', "VXL Life Sciences"),
    (r'\badley lab\b', "Adley Lab"),
    (r'\ballastir\b', "Allastir"),
    (r'\bappasamy\b', "Appasamy Ocular Devices"),
    (r'\bbiozenta\b', "Biozenta Lifescience"),
    (r'\bcalrax\b', "Calrax Healthcare"),
    (r'\bj\.?\s*m\.?\s*laboratories\b|\bj\.?\s*m\b', "J.M. Laboratories"),
    (r'\blifecare neuro\b', "Lifecare Neuro Products"),
    (r'\bmsc chemicals\b', "MSC Chemicals"),
    (r'\barcherchem\b', "Archerchem Healthcare"),
    (r'\bmalladi\b', "Malladi Drugs"),
    (r'\bvenky parenterals\b|\bsriguru\b', "Venky Parenterals"),
    (r'\bmedley\b', "Medley Pharmaceuticals"),
    (r'\bfresenius\b', "Fresenius Kabi"),
    (r'\bhepanex\b', "Hepanex"),
    (r'\bkhandelwal\b', "Khandelwal Laboratories"),
    (r'\bhector\b', "Hector Lifesciences"),
    (r'\blinux\b', "Linux Laboratories"),
    (r'\bmedopharm\b', "Medopharm"),
    (r'\bravian\b', "Ravian Life Science"),
    (r'\bsavvy\b', "Savvy Healthcare"),
    (r'\bsynokem\b', "Synokem Pharmaceuticals"),
    (r'\bunichem\b', "Unichem Laboratories"),
    (r'\bcorona\b', "Corona Remedies"),
    (r'\bapex\b', "Apex Laboratories"),
    (r'\bbelco\b', "Belco Pharma"),
    (r'\bencube\b', "Encube Ethicals"),
    (r'\beugia\b', "Eugia Pharma"),
    (r'\bfranco[- ]indian\b', "Franco-Indian Pharmaceuticals"),
    (r'\bgracure\b', "Gracure Pharmaceuticals"),
    (r'\bhalewood\b', "Halewood Laboratories"),
    (r'\bhimalaya\b', "Himalaya Drug Company"),
    (r'\bjodas\b', "Jodas Expoim"),
    (r'\bkoye\b', "Koye Pharmaceuticals"),
    (r'\bleeford\b', "Leeford Healthcare"),
    (r'\bmedreich\b', "Medreich"),
    (r'\bneiss\b', "Neiss Labs"),
    (r'\bontop\b', "Ontop Pharmaceuticals"),
    (r'\bradiant\b', "Radiant Parenterals"),
    (r'\brpg life\b', "RPG Life Sciences"),
    (r'\brusan\b', "Rusan Pharma"),
    (r'\bsamarth\b', "Samarth Life Sciences"),
    (r'\bswiss parenterals\b', "Swiss Parenterals"),
    (r'\bsymbiotec\b', "Symbiotec Pharmalab"),
    (r'\bsystopic\b', "Systopic Laboratories"),
    (r'\btil\b|\btransgene\b', "Transgene Biotek"),
    (r'\bvenus remedies\b', "Venus Remedies"),
    (r'\bwallace\b', "Wallace Pharmaceuticals"),
    (r'\byarrow\b', "Yarrow Chem Products"),
    (r'\bzeno\b', "Zeno Health"),
    (r'\bzuventus\b', "Zuventus Healthcare")
]

def standardize_company_name(comp):
    """Clean and standardize an applicant company name."""
    if not comp:
        return "Unknown"
    comp_clean = comp.strip()

    # 1. Strip Indian honorific legal prefixes: M/s., M/S., M/s, M/S, Messrs., Messrs
    # Notice: we require the slash '/' so it NEVER strips 'MS' from 'MSN' or 'MSD'!
    comp_clean = re.sub(r'^\s*(m/s\.?|messrs\.?)\s*', '', comp_clean, flags=re.I).strip()

    # 2. Check canonical rules with word boundary matching
    comp_lower = comp_clean.lower()
    for pattern, std_name in COMPANY_RULES:
        if re.search(pattern, comp_lower):
            return std_name

    # 3. Clean trailing unit/division descriptors
    clean = comp_clean
    clean = re.sub(r'\s*-\s*unit.*', '', clean, flags=re.I)
    clean = re.sub(r',\s*unit.*', '', clean, flags=re.I)
    clean = re.sub(r'\(.*division.*\)', '', clean, flags=re.I)
    clean = re.sub(r'div\..*', '', clean, flags=re.I)
    
    # 4. Clean corporate legal suffixes (e.g. Pvt Ltd, Limited, Inc, LLP)
    # Notice: (?<!&) prevents stripping 'Co' from 'Arun & Co' or 'G. Loucatos & Co'
    clean = re.sub(r'(?<!&)\s*\b(pvt\.?|ltd\.?|limited|private|inc\.?|llp|corp\.?|corporation)\b', '', clean, flags=re.I)
    clean = re.sub(r'[,\.\-\s]+$', '', clean)
    clean = re.sub(r'^[,\.\-\s]+', '', clean)
    clean = re.sub(r'\s{2,}', ' ', clean)

    # 5. Convert ALL CAPS to Clean Title Case if all capital letters
    if clean.isupper() and len(clean) > 3:
        clean = clean.title()

    return clean.strip() if clean.strip() else comp.strip()

def run_migration():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT COUNT(DISTINCT company_std) FROM approvals")
    before_distinct = c.fetchone()[0]

    c.execute("SELECT id, company FROM approvals")
    rows = c.fetchall()

    updates = []
    for row_id, raw_comp in rows:
        std = standardize_company_name(raw_comp)
        updates.append((std, row_id))

    c.executemany("UPDATE approvals SET company_std = ? WHERE id = ?", updates)
    conn.commit()

    c.execute("SELECT COUNT(DISTINCT company_std) FROM approvals")
    after_distinct = c.fetchone()[0]

    print(f"Migration completed successfully!")
    print(f"Total rows updated: {len(updates)}")
    print(f"Distinct company_std before: {before_distinct} -> after: {after_distinct}")

    # Inspect MSN Group
    c.execute("SELECT company_std, COUNT(*) FROM approvals WHERE company_std LIKE '%MSN%' GROUP BY company_std")
    print("\nMSN Group in database:")
    for r in c.fetchall():
        print("  ", r)

    # Inspect Shilpa Medicare
    c.execute("SELECT company_std, COUNT(*) FROM approvals WHERE company_std LIKE '%Shilpa%' GROUP BY company_std")
    print("\nShilpa Medicare in database:")
    for r in c.fetchall():
        print("  ", r)

    # Inspect Optimus Pharma
    c.execute("SELECT company_std, COUNT(*) FROM approvals WHERE company_std LIKE '%Optimus%' GROUP BY company_std")
    print("\nOptimus Pharma in database:")
    for r in c.fetchall():
        print("  ", r)

    # Inspect Metrochem
    c.execute("SELECT company_std, COUNT(*) FROM approvals WHERE company_std LIKE '%Metrochem%' GROUP BY company_std")
    print("\nMetrochem API in database:")
    for r in c.fetchall():
        print("  ", r)

    # Verify no M/s prefixes remain in company_std
    c.execute("SELECT company_std, COUNT(*) FROM approvals WHERE company_std LIKE 'M/s%' OR company_std LIKE 'M/S%' GROUP BY company_std")
    remaining_ms = c.fetchall()
    print(f"\nRemaining M/s entries in company_std: {len(remaining_ms)}")
    for r in remaining_ms:
        print("  ", r)

    conn.close()

if __name__ == "__main__":
    run_migration()
