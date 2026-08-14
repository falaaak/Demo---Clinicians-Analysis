import pandas as pd
import numpy as np
from thefuzz import fuzz

def prep_data():
    print("Loading raw_data.pkl...")
    df = pd.read_pickle('raw_data.pkl')
    
    # Filter out 'test doctor'
    df = df[~df['Doctor Clean'].astype(str).str.lower().str.contains('test doctor', na=False)]
    
    print("Loading Referrer_Details (1).xls for Marketing Executives...")
    ref_tables = pd.read_html('Referrer_Details (1).xls', header=0)
    ref_df = ref_tables[0]
    
    # Create mapping for Mark_Exec and Degree/Speciality
    mark_exec_map = {}
    deg_map = {}
    
    for _, row in ref_df.iterrows():
        name = str(row.get('Ref_name', '')).strip().upper()
        if not name or name == 'NAN': continue
        
        exec_name = row.get('Mark_Exec')
        deg = row.get('Qualif')
        spl = row.get('Spl_Code')
        
        if pd.notna(exec_name):
            mark_exec_map[name] = str(exec_name).strip()
            
        qual_str = ""
        if pd.notna(deg) and str(deg).strip() and str(deg).strip().upper() != 'NAN':
            qual_str = str(deg).strip()
        if pd.notna(spl) and str(spl).strip() and str(spl).strip().upper() != 'NAN':
            if qual_str:
                qual_str += " - " + str(spl).strip()
            else:
                qual_str = str(spl).strip()
                
        if qual_str:
            deg_map[name] = qual_str
            
    # Filter Outliers (MCH, IMCH, etc.)
    outlier_keywords = ['MCH', 'IMCH', 'BMH', 'KMCT', 'HAIR', 'ESI', 'HOSPITAL', 'HOSP', 'CLINIC', 'LAB', 'LABS', 'CARE', 'HEALTHCARE']
    def is_outlier(name):
        name_upper = name.upper()
        for kw in outlier_keywords:
            if kw in name_upper.split() or name_upper.startswith(kw + '-') or name_upper.startswith(kw + ' '):
                return True
        return False
        
    df['Is_Outlier'] = df['Doctor Clean'].apply(is_outlier)
    
    outliers_df = df[df['Is_Outlier'] == True].copy()
    main_df = df[df['Is_Outlier'] == False].copy()
    
    # Consolidate main_df names like we did before
    print("Consolidating names for main dataset...")
    
    unique_docs = main_df['Doctor Clean'].unique()
    doc_frequency = main_df['Doctor Clean'].value_counts()
    
    canonical_map = {}
    processed = set()
    
    for i, doc1 in enumerate(unique_docs):
        if doc1 in processed: continue
        
        group = [doc1]
        for doc2 in unique_docs[i+1:]:
            if doc2 in processed: continue
            if fuzz.token_sort_ratio(doc1, doc2) > 90:
                group.append(doc2)
                
        canonical = max(group, key=lambda d: doc_frequency.get(d, 0))
        for d in group:
            canonical_map[d] = canonical
            processed.add(d)
            
    main_df['Doctor Name'] = main_df['Doctor Clean'].map(canonical_map)
    
    # Consolidate outliers_df names as well
    print("Consolidating names for outliers dataset...")
    unique_outliers = outliers_df['Doctor Clean'].unique()
    outlier_frequency = outliers_df['Doctor Clean'].value_counts()
    
    outlier_canonical_map = {}
    outlier_processed = set()
    
    for i, out1 in enumerate(unique_outliers):
        if out1 in outlier_processed: continue
        
        group = [out1]
        for out2 in unique_outliers[i+1:]:
            if out2 in outlier_processed: continue
            # token_sort_ratio handles MCH - Neuro vs MCH Neuro well
            if fuzz.token_sort_ratio(out1, out2) > 90:
                group.append(out2)
                
        canonical = max(group, key=lambda d: outlier_frequency.get(d, 0))
        for d in group:
            outlier_canonical_map[d] = canonical
            outlier_processed.add(d)
            
    outliers_df['Doctor Clean'] = outliers_df['Doctor Clean'].map(outlier_canonical_map)

    # Apply maps to canonical names
    main_df['Mark_Exec'] = main_df['Doctor Name'].map(mark_exec_map).fillna(np.nan)
    
    # Manual assignments from user request
    jishnu_docs = [
        'AABU ALEX THOMAS.', 'SUDHEER.M.', 'ABDUREHIMAN.K.P.,', 
        'SAMEER SAKKEER HUSSAIN', 'SABITHA NITHYANANDAN', 'CHANDHU.A.S', 
        'BIJU.I.K.', 'VISHNUPRIYA.A.R', 'BIJOY.K.', 'ZAKEER.N.P', 'SREEJITH.K.'
    ]
    main_df.loc[main_df['Doctor Name'].isin(jishnu_docs), 'Mark_Exec'] = 'JISHNU'
    
    vishnu_docs = [
        'ROJITH K BALAKRISHNAN', 'JUBIN KAMAR.', 'SARFARAZ ASLAM.', 'DAISY THOMAS',
        'NASEER ALI.', 'VIJAY K ASHOK.', 'BINOY.J.PAUL.', 'VINUGOPAL.S.',
        'ALTAF ALI NAUSHAD', 'JOMY VADASSERIL JOSE.', 'ATHUL PAUL'
    ]
    main_df.loc[main_df['Doctor Name'].isin(vishnu_docs), 'Mark_Exec'] = 'Vishnu P'
    
    prashob_docs = [
        'ANISH KUMAR,', 'RADHAMANI.M', 'ARUN SIVASANKAR', 'ANEES MANNATH.',
        'REJU.V.K.', 'JITHESH.K.', 'RAMACHANDRAN.T.M.', 'TINOY PAUL.',
        'NUZIL MOOPAN', 'BALA GUHAN.', 'BINILA JOSE', 'SIJITH.K.R.', 'BEENA GUHAN.',
        'BELSY CLETUS', 'MINU JAYAN.', 'SHYAM PRASAD.P.V,', 'SALVINE E JOHN',
        'VINAYACHANDRAN NAIR', 'SHILPA M MANUEL', 'RAJEEVAN.P.R.', 'MADHU.K..',
        'MOHAMMED RAFEEQUE.P.K.'
    ]
    main_df.loc[main_df['Doctor Name'].isin(prashob_docs), 'Mark_Exec'] = 'PRASHOB TP'
    
    main_df['Degree'] = main_df['Doctor Name'].map(deg_map).fillna('')
    
    print("Saving processed data...")
    main_df.to_pickle('dashboard_data.pkl')
    outliers_df.to_pickle('outliers_data.pkl')
    print("Done!")

if __name__ == '__main__':
    prep_data()
