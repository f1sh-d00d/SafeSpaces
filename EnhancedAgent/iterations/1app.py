from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from sentence_transformers import SentenceTransformer
from langchain.vectorstores.faiss import FAISS
from langchain.docstore import InMemoryDocstore
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from ollama import chat
import numpy as np
import streamlit as st
import PyPDF2
import json
import csv
import faiss

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize FAISS index for file embeddings
faiss_index = None

#initialize docstore variables
docstore = None
index_to_docstore_id = None


def embedding_function(texts):
    return generate_embeddings(texts)


def generate_embeddings(content_list):
    '''Given a list of file contents, create embeddings'''
    embeddings = embedding_model.encode(content_list)
    return np.array(embeddings)

def index_embeddings(embeddings):
    '''Index given embeddings with FAISS'''
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def vectorize(file, index=None, docstore=None, index_to_docstore_id=None):
    '''Given a file, chunk it, create embeddings for its chunks, and add it to the FAISS index.'''
    content = ""

    # Determine file type
    file_type = file.name.split('.')[-1]

    # Extract content based on file type
    if file_type == "txt":
        content = file.read().decode('utf-8')
    
    elif file_type == "csv":
        content = file.read().decode('utf-8')
        # Convert CSV content to plain text for embedding
        csv_reader = csv.reader(content.splitlines())
        content = "\n".join([" ".join(row) for row in csv_reader])

    elif file_type == "json":
        content = file.read().decode('utf-8')
        json_data = json.loads(content)
        content = json.dumps(json_data, indent=2)
    
    elif file_type == "pdf":
        reader = PyPDF2.PdfReader(file)
        content = "\n".join([page.extract_text() for page in reader.pages])
    
    # Check for empty content
    if not content:
        st.error("Failed to extract file content")
    else:
        # Chunk the file content for better embedding generation
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_text(content)

        # Generate embeddings for the chunks
        embeddings = generate_embeddings(chunks)

        # Initialize FAISS index if not already present
        if index is None:
            index = index_embeddings(embeddings)
            docstore = InMemoryDocstore({str(i): Document(page_content=chunk) for i, chunk in enumerate(chunks)})
            index_to_docstore_id = {i: str(i) for i in range(len(chunks))}
        else:
            index.add(embeddings)  # Add new embeddings to the index
            doc_ids = [str(i + len(index_to_docstore_id)) for i in range(len(chunks))]
            new_docs ={doc_id: Document(page_content=chunk) for doc_id, chunk in zip(doc_ids, chunks)}
            docstore._documents.update(new_docs)
            index_to_docstore_id.update({i + len(index_to_docstore_id): doc_id for i, doc_id in enumerate(doc_ids)})

        st.write(f"File '{file.name}' has been embedded and added to the vector store.")
    
    return index, docstore, index_to_docstore_id

# Initialize Langchain agent
def create_agent(llama_model, faiss_index, docstore, index_to_docstore_id):
    # Define prompt template for LLaMA's response
    prompt_template = """You are an intelligent assistant.
    
    You will receive a user query and optionally a list of related content. 
    Based on the relevance of the content, generate a response.

    Query: {query}

    If relevant, augment your response with the uploaded file contents. Otherwise, respond independently."""

    # Initialize a ConversationalRetrievalChain with FAISS
    retriever = FAISS(embedding_function, faiss_index, docstore, index_to_docstore_id)

    agent = ConversationalRetrievalChain.from_llm(
        llm=llama_model,
        retriever=retriever,
        prompt=PromptTemplate(template=prompt_template, input_variables=["query"])
    )
    
    return agent


def get_response(agent, prompt):
    # Vectorize the user query
    query_embedding = embedding_model.encode([prompt])
    
    # Search the FAISS index for relevant content
    distances, indices = search_index(faiss_index, query_embedding)

    # Define a threshold for relevance (you can adjust this)
    threshold = 0.5
    if len(distances) > 0 and distances[0][0] < threshold:
        # If relevant, pass the prompt and relevant file content to LLaMA 3.2
        response = agent({'query': prompt})
    else:
        # If not relevant, only pass the prompt to LLaMA 3.2
        response = chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    
    return response['message']['content']


#___BEGIN APP___
uploaded_files = []
faiss_index = None  # Initialize FAISS index for embeddings

st.title("LLaMA 3.2 Chat with Augmented File Search")

uploaded = st.file_uploader("Upload a file to augment the model", type=["csv", "pdf", "json", "txt"], accept_multiple_files=False)

if uploaded is not None:
    # Save uploaded file to bank
    uploaded_files.append(uploaded)
    print(f"{uploaded.name} uploaded successfully.")
    # Vectorize and add to FAISS index
    faiss_index, docstone, index_to_docstore_id = vectorize(uploaded, faiss_index)

# Chat input and response handling (as before)
if prompt := st.chat_input("Ask something"):
    if faiss_index is not None:
        agent = create_agent("llama3.2", faiss_index, docstore, index_to_docstore_id)
        assistant_response = get_response(agent, prompt)
    else:
        assistant_response = chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])['message']['content']

    # Display the assistant's response
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

    # Save assistant message to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
