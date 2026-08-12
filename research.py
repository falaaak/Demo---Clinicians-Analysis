import pandas as pd
import pickle

print("Loading raw_data...")
df = pd.read_pickle('raw_data.pkl')

print("Sample doctors:")
print(df['Doctor Clean'].unique()[:20])

print("Checking for MCH:")
mch_docs = df[df['Doctor Clean'].str.contains('MCH', na=False, case=False)]['Doctor Clean'].unique()
print(mch_docs)

print("Loading Referrer details for Mark_Exec...")
try:
    tables = pd.read_html('Referrer_Details (1).xls', header=0)
    ref_df = tables[0]
    print("Columns in ref:", ref_df.columns.tolist())
    print("Sample Mark_Exec:", ref_df[['Ref_name', 'Mark_Exec']].head(10))
except Exception as e:
    print(e)
