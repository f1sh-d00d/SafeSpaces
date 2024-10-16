import streamlit as st
import pandas as pd
from parsers import parse_file
from embeddings import generate_embeddings, index_embeddings
from chat import ollama_chat

st.title("Brade's Faves v.alpha 1.0.0")

# Upload a file
uploaded_file = st.file_uploader("Upload a file (csv, json, pdf, txt)", type=["csv", "pdf", "json", "txt"])

def save_chat_history_to_csv(messages, filename="chat_history.csv"):
    df = pd.DataFrame(messages)
    df.to_csv(filename, index=False)

if uploaded_file:
    # Parse file content
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

        # Get the model's response
        response = ollama_chat(user_input, faiss_index, file_embeddings, [file_content], "llama3.1", st.session_state.messages)

        # Show the assistant's response
        with st.chat_message("assistant"):
            st.markdown(response)

        # Add response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Save chat history to CSV
        save_chat_history_to_csv(st.session_state.messages)