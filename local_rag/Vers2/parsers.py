import pandas as pd
import json
from PyPDF2 import PdfReader

def parse_file(file):
    extension = file.name.split('.')[-1].lower()

    if extension == "csv":
        df = pd.read_csv(file)
        json_data = df.to_dict(orient='records') #converts csv to JSON for easier embedding and more accurate queries
        return json.dumps(json_data, indent=2) #return JSON formatted string
    
    elif extension == "json":
        data = json.load(file)
        return json.dumps(data, indent=2) #converts json into a formatted string

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
