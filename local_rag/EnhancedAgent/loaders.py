from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from io import StringIO
import PyPDF2
import csv
import json


def load(file, doc_store):
    if file.type == 'application/pdf':
        loadPDF(file, doc_store)
    
    elif file.type == 'text/plain':
        loadTXT(file, doc_store)

    elif file.type == 'application/json':
        loadJSON(file, doc_store)

    elif file.type == 'text/csv':
        loadCSV(file, doc_store)
       

def loadPDF(file, doc_store):
    documents = []
    reader = PyPDF2.PdfReader(file)
    text = "\n".join([page.extract_text() for page in reader.pages])

    #remove newline characters
    text = text.replace('\n', ' ')

    #initialize text splitter object
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, length_function=len, is_separator_regex=False)
    #chunk text
    chunks = text_splitter.split_text(text)
    #print(f"CHUNKS: {chunks}")

    #create list of documents from text chunks
    documents = [Document(page_content=chunk) for chunk in chunks]
    
    for doc in documents:
        doc_store.append(doc)


def loadTXT(file, doc_store):
    text = file.read().decode('utf-8')
    text = text.replace('\n', ' ')
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, length_function=len, is_separator_regex=False)
    chunks = text_splitter.split_text(text)
    
    documents = [Document(page_content=chunk) for chunk in chunks]
    for doc in documents:
        doc_store.append(doc)

def loadJSON(file, doc_store):
    json_content = json.loads(file.read().decode('utf-8'))
    text = json.dumps(json_content, indent=2)
    text = text.replace('\n', ' ')
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, length_function=len, is_separator_regex=False)
    chunks = text_splitter.split_text(text)
    
    documents = [Document(page_content=chunk) for chunk in chunks]
    for doc in documents:
        doc_store.append(doc)


def loadCSV(file, doc_store):
    #decode csv file into a string
    csv_content = file.read().decode('utf-8')
    #turn file into a dict, with StringIO using the string like a file object
    csv_reader = csv.DictReader(StringIO(csv_content))

    text=""
    for row in csv_reader:
        text += f"{row}\n"

    text = text.replace('\n', ' ')

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, length_function=len, is_separator_regex=False)
    chunks = text_splitter.split_text(text)
    
    documents = [Document(page_content=chunk) for chunk in chunks]
    for doc in documents:
        doc_store.append(doc)


