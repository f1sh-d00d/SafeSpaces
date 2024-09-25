import streamlit as st
from parsers import parse_file
from embeddings import generate_embeddings, index_embeddings
from chat import ollama_chat

st.title("RAG Model with LLaMA 3.1")

# Upload a file
uploaded_file = st.file_uploader("Upload a file (csv, json, pdf, txt)", type=["csv", "pdf", "json", "txt"])

if uploaded_file:
    # Parse file content
    file_content = parse_file(uploaded_file)
    st.write("File uploaded and content extracted!\n", file_content)

    # Generate embeddings for the file content
    file_embeddings = generate_embeddings([file_content])
    st.write("Shape: ", file_embeddings.shape)

    # Index the embeddings in FAISS
    faiss_index = index_embeddings(file_embeddings)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input and respond
    if user_input := st.chat_input("Ask something about the file"):
        # Show user's input
        with st.chat_message("user"):
            st.markdown(user_input)

        # Add user input to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get the model's response
        response = ollama_chat(user_input, faiss_index, file_embeddings, [file_content], "llama3.1", st.session_state.messages)

        # Show the assistant's response
        with st.chat_message("assistant"):
            st.markdown(response)

        # Add response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
