from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from uuid import uuid4
import streamlit as st
import loaders
import faiss

st.title("Llama3.2 Local Rag with Ollama")

#intialize doc store to hold loaded documents
doc_store = []

# Upload a file
uploaded_files = st.file_uploader("Upload a file (csv, json, pdf, txt)", type=["csv", "pdf", "json", "txt"], accept_multiple_files=True)

if uploaded_files:
    #Load uploaded file
    for file in uploaded_files:
        loaders.load(file, doc_store)

print(f"Doc Store: {doc_store}")

#initialize a function to embed documents and queries
embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

#set up an index that everything will be stored and retrieved with
index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

#initialize vector store
vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

if len(doc_store) > 0:
    #set up ids for documents
    uuids = [str(uuid4()) for _ in range(len(doc_store))]

    #embed documents and add them to vector store
    vector_store.add_documents(documents=doc_store, ids=uuids)
    print(f"Vector Store: {vector_store}")


'''
    file_content = parse_file(uploaded_file)
    st.write("File uploaded and content extracted!")
    
    # Generate embeddings for the file content
    file_embeddings = generate_embeddings([file_content])
    
    # Index the embeddings in FAISS
    faiss_index = index_embeddings(file_embeddings)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "Context:" in message["content"]:
                content_list = message["content"].split()
                #print("\nLIST:\n", content_list)
                i = content_list.index("Context:")
                st.markdown(" ".join(content_list[:i]))
            else:
                st.markdown(message["content"])
    
    # Accept user input and respond
    if user_input := st.chat_input("Ask something about the file"):
        # Show user's input
        with st.chat_message("user"):
            st.markdown(user_input)

        # Add user input to chat history
        #st.session_state.messages.append({"role": "user", "content": user_input})

        # Get the model's response
        response = ollama_chat(user_input, faiss_index, file_embeddings, [file_content], "llama3.2", st.session_state.messages)

        # Show the assistant's response
        with st.chat_message("assistant"):
            st.markdown(response)

        # Add response to chat history
        #st.session_state.messages.append({"role": "assistant", "content": response})
        '''
