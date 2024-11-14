from langchain.text_splitter import CharacterTextSplitter
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import streamlit as st
from ollama import chat
import PyPDF2
import json
import csv


def faiss_search_tool(query, index, k=3):
    '''A tool for a langchain agent to search an FAISS index with a query embedding'''
    #generate query embedding
    quert_embedding = generate_embeddings([query])[0]

    #search FAISS index
    distances, indices = search_index(index, query_embedding, top_k=k)

    #process search results (return closest matching text chunks)
    results = [uploaded_files[i].name for i in indices[0]]

    return results


def llama_tool(query):
    response = chat(model="llama3.2", messages=[{"role": "user", "content": query}])
    return response['message']['content']


def is_relevant(query, index, threshold=0.5):
    '''Check to see if query is relevant to files uploaded'''
    query_embedding = generate_embeddings([query])[0]
    distances, _ = search_index(index, query_embedding, top_k=1)

    #if the query compared to the index is below the threshold, it is relevant
    return distances[0][0] < threshold


def agent_decide(query, index):
    if is_relevant(query, index):
        return faiss_tool.func(query)
    else:
        return llama_agent_tool.func(query)


def generate_embeddings(content_list):
    '''Give a list containing the contents of a file, embed the content into a numby array'''
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(content_list)
    return np.array(embeddings)


def index_embeddings(embeddings):
    '''index given embeddings with FAISS'''
    #get the dimension of the array
    dimension = embeddings.shape[1]

    #set dimension as distance for similarity search
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index


def search_index(index, query_embedding, top_k=3):
    #ensure query has proper dimension for FAISS search
    query_embedding = np.array(query_embedding).reshape(1,-1)

    #perform the search
    distances, indices = index.search(query_embedding, top_k)
    return distances, indices

def vectorize(file, index=None):
    '''given a file, chunk it, create embeddings for it's chunks, and add it to the Chroma vector store. Takes a file and a FAISS index'''
    content = ""

    #get the file extension
    file_type = file.name.split('.')[-1]

    #extract content based on file type
    if file_type == "txt":
        content = file.read().decode('utf-8')
    
    elif file_type == "csv":
        content = file.read().decode('utf-8')

        #extract text from csv content (this may need edited later into some sort of dictionary creation)
        csv_reader = csv.reader(content.splitlines())
        content = "\n".join([" ".join(row) for row in csv_reader])

    elif file_type == "json":
        content = file.read().decode('utf-8')
        json_data = json.loads(content)
        content = json.dumps(json_data, indent=2)
    
    elif file_type == "pdf":
        reader = PyPDF2.PdfReader(file)
        content = "\n".join([page.extract_text() for page in reader.pages])
    
    #check for empty content
    if not content:
        st.error("Failed to extract file content")
    else:
        #chunk file
        print("File content extracted")
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_text(content)
        print("Chunks generated")

        #create embeddings for the chunks
        print(chunks)
        embeddings = generate_embeddings(chunks)
        print(f"Embeddings shape: {embeddings.shape}")

        if index is None:
            #create index if it doens't already exist
            index = index_embeddings(embeddings)
        else:
            index.add(embeddings)
        print("Embeddings created and added to store")
    return index



faiss_tool = Tool(
        name="FAISS Seach",
        func=lambda query: faiss_search_tool(query, faiss_index),
        description="Searches file embeddings using FAISS"
)


llama_agent_tool = Tool(
        name="Llama",
        func=lambda query: llama_tool(query),
        description="Responds to user input with llama model"
)


tools = [faiss_tool, llama_agent_tool]




agent = initialize_agent(
        tools=tools,
        llm = "llama3.2",
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)



#init FAISS index (if needed)
faiss_index = None

#File bank for the model to reference
uploaded_files = []


st.title("Llama 3.2 chat with Ollama")

#import a file, one at a time
uploaded = st.file_uploader("Please enter a file to augment the model", type=["csv", "pdf", "json", "txt"], accept_multiple_files=False)

if uploaded is not None:
    '''Whenever a new file is uploaded, chunk it, create an embedding for it, and add it the Chroma vector store'''
    #save uploaded file to bank
    uploaded_files.append(uploaded)
    st.write(f"{uploaded.name} uploaded successfully.")
    vectorize(uploaded, faiss_index)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages from chat history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask something"):
     # Display user message in chat
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run agent to decide whether to query FAISS or use LLaMA
    response = agent_decide(prompt, faiss_index)

    # Display assistant's response
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Add assistant message to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
