import pdfplumber
import re

pdf_path = "Doctors Data/August 2025 (1).pdf"
data = []
current_doctor = None

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if not text:
            continue
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Match doctor name line: "1 (Major)SAPNA S NAMBIAR."
            # Actually, the index can be any number. So `\d+ (.+)` might match tests too.
            # But tests have "Amount" at the end, and doctor lines don't have amounts.
            # Wait, Doctor Total line: "(Major)SAPNA S NAMBIAR. Total 8 2,990.00"
            
            # Let's print out lines that don't match the test pattern.
            pass

print("Sample parsed data logic is ready to be tested.")
