import os
import re
import pandas as pd
import pdfplumber
from thefuzz import fuzz

DATA_DIR = "Doctors Data"
REF_FILE = "Referrer_Details (1).xls"

def load_reference_data():
    try:
        tables = pd.read_html(REF_FILE, header=0)
        df_ref = tables[0]
        # Clean names and map to degree
        ref_dict = {}
        for _, row in df_ref.iterrows():
            name = str(row.get('Ref_name', '')).strip().upper()
            deg = str(row.get('Qualif', '')).strip()
            if deg.lower() == 'nan': deg = ''
            if name:
                ref_dict[name] = deg
        return ref_dict
    except Exception as e:
        print(f"Error reading reference data: {e}")
        return {}

def is_institution(name):
    keywords = ['HOSPITAL', 'LAB', 'CAMP', 'CLINIC', 'CENTER', 'CENTRE', 'CARE', 'MEDICAL', 'SCAN', 'TRUST', 'POLY CLINIC', 'NURSING HOME']
    name_upper = name.upper()
    for kw in keywords:
        # Check if the word is a distinct word to avoid false positives (e.g. Scantlebury -> SCAN)
        if re.search(r'\b' + kw + r'\b', name_upper):
            return True
    return False

def clean_doctor_name(name):
    # Remove standard prefixes like (Major), DR., Dr
    name = re.sub(r'^\(?(Major|Minor|Dr\.?|DR\.?|PROF\.?)\)?\s*', '', name, flags=re.IGNORECASE)
    # Remove leading numbers if accidentally captured
    name = re.sub(r'^\d+\s+', '', name)
    return name.strip().upper()

def extract_month_from_filename(filename):
    match = re.match(r'([a-zA-Z]+ \d{4})', filename)
    if match:
        return match.group(1)
    return filename

def parse_pdf(filepath):
    month = extract_month_from_filename(os.path.basename(filepath))
    records = []
    
    current_doctor = None
    current_tests = []
    
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text: continue
            
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                
                # Check for "Total" line which signifies end of a doctor's record block
                total_match = re.search(r'^(.*?) Total\s+(\d+)\s+([\d,]+\.\d{2})$', line)
                if total_match:
                    doc_raw_name = total_match.group(1).strip()
                    total_vol = int(total_match.group(2))
                    total_amount = float(total_match.group(3).replace(',', ''))
                    
                    doc_clean = clean_doctor_name(doc_raw_name)
                    
                    if not is_institution(doc_clean):
                        records.append({
                            'Month': month,
                            'Doctor Raw': doc_raw_name,
                            'Doctor Clean': doc_clean,
                            'Total Volume': total_vol,
                            'Total Amount': total_amount,
                            'Tests': current_tests
                        })
                    
                    current_doctor = None
                    current_tests = []
                    continue
                
                # Match a test line: "1 COMPLETE HAEMOGRAM 1 250.00"
                # It starts with a number, then test name, then count, then amount
                test_match = re.match(r'^\d+\s+(.*?)\s+(\d+)\s+([\d,]+\.\d{2})$', line)
                if test_match and current_doctor:
                    test_name = test_match.group(1).strip()
                    test_count = int(test_match.group(2))
                    test_amount = float(test_match.group(3).replace(',', ''))
                    current_tests.append({
                        'Test Name': test_name,
                        'Count': test_count,
                        'Amount': test_amount
                    })
                    continue
                
                # If it doesn't match a test or total, and we don't have a current doctor,
                # it might be a doctor name header line: e.g. "1 (Major)SAPNA S NAMBIAR."
                doc_match = re.match(r'^\d+\s+(.+)$', line)
                if doc_match and not current_doctor:
                    # Could be headers, ignore known header strings
                    possible_doc = doc_match.group(1).strip()
                    if "Test Name" not in possible_doc and "Referrer" not in possible_doc:
                        current_doctor = possible_doc
                        current_tests = []
                        
    return records

def find_duplicates(df):
    unique_docs = df['Doctor Clean'].unique()
    duplicates = []
    processed = set()
    
    # We will compute a simple "test signature" for each doctor (Top 5 tests)
    doc_signatures = {}
    for doc in unique_docs:
        doc_tests = df[df['Doctor Clean'] == doc]['Tests'].tolist()
        # flatten
        all_tests = []
        for test_list in doc_tests:
            all_tests.extend([t['Test Name'] for t in test_list])
        
        from collections import Counter
        top_tests = [k for k, v in Counter(all_tests).most_common(5)]
        doc_signatures[doc] = ", ".join(top_tests)
        
    group_id = 1
    for i, doc1 in enumerate(unique_docs):
        if doc1 in processed:
            continue
            
        group = [doc1]
        for doc2 in unique_docs[i+1:]:
            if doc2 in processed:
                continue
            # Check fuzzy match
            score = fuzz.token_sort_ratio(doc1, doc2)
            if score > 85: # Threshold for similarity
                group.append(doc2)
                
        if len(group) > 1:
            for doc in group:
                duplicates.append({
                    'Group ID': group_id,
                    'Doctor Name': doc,
                    'Similarity Score': score if doc != group[0] else 100,
                    'Top Tests (Signature)': doc_signatures[doc]
                })
                processed.add(doc)
            group_id += 1
        else:
            processed.add(doc1)
            
    return pd.DataFrame(duplicates)

def main():
    print("Loading reference data...")
    ref_data = load_reference_data()
    
    all_records = []
    print("Parsing PDFs...")
    for file in os.listdir(DATA_DIR):
        if file.endswith('.pdf'):
            filepath = os.path.join(DATA_DIR, file)
            print(f"  Parsing {file}...")
            records = parse_pdf(filepath)
            all_records.extend(records)
            
    df = pd.DataFrame(all_records)
    print(f"Extracted {len(df)} total monthly doctor records (excluding institutions).")
    
    # Map degrees
    df['Degree'] = df['Doctor Clean'].apply(lambda x: ref_data.get(x, ''))
    
    # Save the raw compiled data to a pickle for the next step so we don't have to re-parse PDFs
    df.to_pickle('raw_data.pkl')
    
    print("Finding potential duplicates...")
    dup_df = find_duplicates(df)
    
    if not dup_df.empty:
        dup_df.to_excel('potential_duplicates.xlsx', index=False)
        print("Saved 'potential_duplicates.xlsx'.")
    else:
        print("No duplicates found.")

if __name__ == '__main__':
    main()
