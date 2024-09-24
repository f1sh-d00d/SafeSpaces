'''
1. File Types Supported:
   - PDF (.pdf)
   - Text (.txt)
   - JSON (.json)
   - CSV (.csv)

2. Main Functions:
   - `append_to_vault(text)`: Processes and appends text to vault.txt
   - `convert_pdf_to_text()`: Handles PDF file upload and processing
   - `upload_txtfile()`: Handles text file upload and processing
   - `upload_jsonfile()`: Handles JSON file upload and processing
   - `upload_csvfile()`: Handles CSV file upload and processing

3. Text Processing:
   - Normalizes whitespace
   - Splits text into chunks of up to 1000 characters
   - Preserves sentence structure when possible

4. File Handling:
   - Uses `tkinter.filedialog` for file selection
   - Reads files with appropriate encoding (utf-8)

5. Output:
   - Appends processed text to "vault.txt"
   - Each chunk is written on a separate line

6. GUI:
   - Uses Tkinter for a simple graphical interface
   - Separate buttons for uploading each file type

7. Libraries Used:
   - os
   - tkinter
   - PyPDF2
   - re (for regular expressions)
   - json
   - csv

8. Error Handling:
   - Basic checks to ensure a file is selected before processing

9. Modularity:
   - Separate functions for each file type allow for easy maintenance and expansion

10. Consistency:
    - Similar processing approach for all file types
    - Unified method for appending to vault.txt


'''

import os
import tkinter as tk
from tkinter import filedialog
import PyPDF2
import re
import json
import csv
# from langchain.document_loaders import DirectoryLoader 

def append_to_vault(text):
    # Normalize whitespace and clean up text
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split text into chunks by sentences, respecting a maximum chunk size
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 < 1000:
            current_chunk += (sentence + " ").strip()
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk)
    
    with open("vault.txt", "a", encoding="utf-8") as vault_file:
        for chunk in chunks:
            vault_file.write(chunk.strip() + "\n")

def convert_pdf_to_text():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ' '.join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        append_to_vault(text)
        print(f"PDF content appended to vault.txt")

def upload_txtfile():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, 'r', encoding="utf-8") as txt_file:
            text = txt_file.read()
        append_to_vault(text)
        print(f"Text file content appended to vault.txt")

def upload_jsonfile():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, 'r', encoding="utf-8") as json_file:
            data = json.load(json_file)
        text = json.dumps(data, ensure_ascii=False)
        append_to_vault(text)
        print(f"JSON file content appended to vault.txt")

def upload_csvfile():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        with open(file_path, 'r', newline='', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file)
            text = '\n'.join(','.join(row) for row in csv_reader)
        append_to_vault(text)
        print(f"CSV file content appended to vault.txt")
        # print(text)

# Create the main window
root = tk.Tk()
root.title("Upload PDF, JSON, TXT, or CSV")
root.geometry("200x300")
root.config(bg="gray")

# Create buttons for each file type
pdf_button = tk.Button(root, text="Upload PDF", command=convert_pdf_to_text, width=15, height=2, bd=5)
pdf_button.config(font=("#Ink Free", 10, "bold"))
pdf_button.config(bg="#ff575f")
pdf_button.pack(pady=10)

txt_button = tk.Button(root, text="Upload Text File", command=upload_txtfile, width=15, height=2, bd=5)
txt_button.config(font=("#Ink Free", 10, "bold"))
txt_button.config(bg="#57f7ff")
txt_button.pack(pady=10)

json_button = tk.Button(root, text="Upload JSON File", command=upload_jsonfile, width=15, height=2, bd=5)
json_button.config(font=("#Ink Free", 10, "bold"))
json_button.config(bg="#fad96e")
json_button.pack(pady=10)

csv_button = tk.Button(root, text="Upload CSV File", command=upload_csvfile, width=15, height=2, bd=5)
csv_button.config(font=("#Ink Free", 10, "bold"))
csv_button.config(bg="#6efac7")
csv_button.pack(pady=10)

# Run the main event loop
root.mainloop()