import pandas as pd
import pdfplumber
import os

pdf_path = "Doctors Data/August 2025 (1).pdf"
xls_path = "Referrer_Details (1).xls"

print("--- XLS DATA ---")
try:
    df = pd.read_excel(xls_path, engine='xlrd')
    print(df.head())
    print("Columns:", df.columns.tolist())
except Exception as e:
    print("Error reading XLS:", e)

print("\n--- PDF DATA ---")
try:
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        print("Text from first page:")
        print(text[:1000] if text else "No text extracted")
        print("\nTable from first page:")
        tables = first_page.extract_tables()
        if tables:
            for i, table in enumerate(tables):
                print(f"Table {i}:")
                for row in table[:5]:
                    print(row)
        else:
            print("No tables found by pdfplumber")
except Exception as e:
    print("Error reading PDF:", e)
