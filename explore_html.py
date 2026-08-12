import pandas as pd

xls_path = "Referrer_Details (1).xls"

try:
    tables = pd.read_html(xls_path, header=0)
    df = tables[0]
    print("Columns:", df.columns.tolist())
    # find columns that might be Name and Degree
    name_cols = [c for c in df.columns if 'name' in str(c).lower()]
    deg_cols = [c for c in df.columns if 'deg' in str(c).lower() or 'qual' in str(c).lower()]
    print("Potential Name columns:", name_cols)
    print("Potential Degree columns:", deg_cols)
    print("\nSample Data:")
    print(df[name_cols + deg_cols].head(10))
except Exception as e:
    print("Error reading HTML table:", e)
