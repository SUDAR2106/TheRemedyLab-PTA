# test_parser.py
from services.document_parser import DocumentParser

file_path = "path/to/sample_report.pdf"
try:
    data = DocumentParser.parse_report(file_path)
    print("Extracted:", data)
except Exception as e:
    print("Error while parsing:", e)
