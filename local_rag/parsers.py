import pandas as pd
import json
from PyPDF2 import PdfReader

def parse_file(file):
    extension = file.name.split('.')[-1].lower()

    if extension == "csv":
        return pd.read_csv(file).to_json()
    elif extension == "json":
        return json.load(file)
    elif extension == "pdf":
        reader = PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif extension == "txt":
        return file.read().decode('utf-8')
    else:
        return "Unsupported file type"
