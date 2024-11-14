from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from uuid import uuid4
import streamlit as st
import loaders
import faiss

st.title("Llama3.2 Local Rag with Ollama")

#initialize model
ollama_model = Ollama(
    base_url='http://localhost:11434',
    model="llama3.2"
)

#intialize doc store to hold loaded documents
doc_store = []

# Upload a file
uploaded_files = st.file_uploader("Upload a file (csv, json, pdf, txt)", type=["csv", "pdf", "json", "txt"], accept_multiple_files=True)

if uploaded_files:
    #Load uploaded file
    for file in uploaded_files:
        loaders.load(file, doc_store)

#print(f"Doc Store: {doc_store}")

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
    #print(f"Vector Store: {vector_store}")


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
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        #set up empty vault on new question
        vault = []

        #set up a retriever from the vector store
        retriever = vector_store.as_retriever()
        
        #retrieve top 20 relevant Documents (text chunks) according to the user input
        relevant_docs = retriever.invoke(user_input, top_k=20)

        #add docuemnt text to vault
        for doc in relevant_docs:
            vault.append(doc.page_content)

        #turn vault content into one string:
        vault_content = "\n".join(vault)

        #augment user input with vault content:
        augmented_input = f"{user_input}\nContext:\n{vault_content}"


        #set up a chain for the model
        qachain = RetrievalQA.from_chain_type(llm=ollama_model, retriever=retriever)

        #pass user prompt through the chain
        answer = qachain.invoke({"query": augmented_input})

        #extract model response
        response = answer['result']

        # Show the assistant's response
        with st.chat_message("assistant"):
            st.markdown(response)

        # Add response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})


