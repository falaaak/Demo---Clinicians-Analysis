import pandas as pd
from thefuzz import fuzz

def generate_report():
    print("Loading raw data...")
    try:
        df = pd.read_pickle('raw_data.pkl')
    except Exception as e:
        print(f"Error loading raw_data.pkl: {e}")
        return

    # 1. Automate merging of duplicates
    print("Consolidating doctor names...")
    unique_docs = df['Doctor Clean'].unique()
    doc_frequency = df['Doctor Clean'].value_counts()
    
    canonical_map = {}
    processed = set()
    
    for i, doc1 in enumerate(unique_docs):
        if doc1 in processed: continue
        
        group = [doc1]
        for doc2 in unique_docs[i+1:]:
            if doc2 in processed: continue
            if fuzz.token_sort_ratio(doc1, doc2) > 90:
                group.append(doc2)
                
        # The canonical name is the one that appears most frequently
        canonical = max(group, key=lambda d: doc_frequency.get(d, 0))
        for d in group:
            canonical_map[d] = canonical
            processed.add(d)
            
    df['Doctor Merged'] = df['Doctor Clean'].map(canonical_map)
    # Re-map degrees to the canonical name to be consistent
    # Just grab the first non-empty degree found for the group, or let it be
    degree_map = {}
    for canonical in canonical_map.values():
        degrees = df[df['Doctor Merged'] == canonical]['Degree'].dropna().unique()
        valid_degrees = [d for d in degrees if d != '']
        degree_map[canonical] = valid_degrees[0] if valid_degrees else ''
        
    df['Degree'] = df['Doctor Merged'].map(degree_map)
    
    print("Generating Sheet 1...")
    # Sheet 1: Month, Doctors name, Doctors degree, total Billed test volume in that month, total amount billed in that month
    sheet1_df = df.groupby(['Month', 'Doctor Merged', 'Degree']).agg({
        'Total Volume': 'sum',
        'Total Amount': 'sum'
    }).reset_index()
    
    sheet1_df.rename(columns={
        'Doctor Merged': 'Doctor Name',
        'Total Volume': 'Total Billed Test Volume',
        'Total Amount': 'Total Amount Billed'
    }, inplace=True)
    
    # 2. Identify Top 50 doctors by total billed amount (across all months)
    print("Generating Sheet 2...")
    doc_totals = sheet1_df.groupby('Doctor Name')['Total Amount Billed'].sum()
    top_50_docs = doc_totals.nlargest(50).index.tolist()
    
    # For Sheet 2, we need rows for individual tests for these top 50 doctors
    top_50_df = df[df['Doctor Merged'].isin(top_50_docs)]
    
    sheet2_records = []
    
    for _, row in top_50_df.iterrows():
        doc = row['Doctor Merged']
        deg = row['Degree']
        month = row['Month']
        total_month_amount = sheet1_df[(sheet1_df['Doctor Name'] == doc) & (sheet1_df['Month'] == month)]['Total Amount Billed'].sum()
        
        tests = row['Tests']
        for test in tests:
            sheet2_records.append({
                'Month': month,
                'Doctor Name': doc,
                'Doctor Degree': deg,
                'Test Name': test['Test Name'],
                'Test Count': test['Count'],
                'Test Amount Billed': test['Amount'],
                'Total Billed Amount in Month': total_month_amount
            })
            
    sheet2_df = pd.DataFrame(sheet2_records)
    
    # We might have multiple entries for the same test for a doctor in a month (if they were merged from slight name variations)
    # Let's aggregate them
    sheet2_df = sheet2_df.groupby(['Month', 'Doctor Name', 'Doctor Degree', 'Test Name']).agg({
        'Test Count': 'sum',
        'Test Amount Billed': 'sum',
        'Total Billed Amount in Month': 'first' # Since it's the same for the month
    }).reset_index()
    
    # Sort for better readability
    sheet1_df.sort_values(by=['Month', 'Total Amount Billed'], ascending=[True, False], inplace=True)
    sheet2_df.sort_values(by=['Doctor Name', 'Month', 'Test Count'], ascending=[True, True, False], inplace=True)
    
    print("Saving to Master_Dataset.xlsx...")
    with pd.ExcelWriter('Master_Dataset.xlsx') as writer:
        sheet1_df.to_excel(writer, sheet_name='Monthly Summary', index=False)
        sheet2_df.to_excel(writer, sheet_name='Top 50 Doctors Detailed', index=False)
        
    print("Done! Master_Dataset.xlsx has been created.")

if __name__ == "__main__":
    generate_report()
