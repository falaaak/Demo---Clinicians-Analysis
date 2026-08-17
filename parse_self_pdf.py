import pdfplumber
import re
import pandas as pd
from datetime import datetime

pdf_path = 'April Self 2.pdf'
records = []
current_month = None

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        
        # Look for date range header
        date_match = re.search(r'Between (\d{2}/\d{2}/\d{4}) And', text)
        if date_match:
            date_str = date_match.group(1)
            dt = datetime.strptime(date_str, "%d/%m/%Y")
            current_month = dt.strftime("%B %Y")
            
        if not current_month:
            continue
            
        for line in text.split('\n'):
            line = line.strip()
            if 'Self Total' in line or 'Grand Total' in line:
                continue
                
            # Example: "1 LIVER FUNCTION TEST 682 341,000.00"
            match = re.match(r'^\s*(\d+)\s+(.*?)\s+(\d+)\s+([\d,]+\.\d{2})$', line)
            if match:
                test_name = match.group(2).strip()
                # Ignore the "Self" heading which looks like "1 Self" 
                # Wait, "1 Self" wouldn't match the 4 groups.
                count = int(match.group(3))
                amount = float(match.group(4).replace(',', ''))
                
                records.append({
                    'Month': current_month,
                    'Test Name': test_name,
                    'Test Count': count,
                    'Test Amount': amount
                })

df = pd.DataFrame(records)
print(df.head())
print(df['Month'].unique())
print(f"Total Amount: {df['Test Amount'].sum():,.2f}")
df.to_pickle('self_data.pkl')
print("Saved to self_data.pkl")
