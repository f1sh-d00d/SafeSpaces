from sentence_transformers import SentenceTransformer
from embeddings import search_index
import ollama
import streamlit as st

# Use SentenceTransformer for embeddings
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def ollama_chat(user_input, faiss_index, vault_embeddings, vault_content, ollama_model, conversation_history):
    # Generate embedding of the user's input using SentenceTransformer
    input_embedding = embedding_model.encode([user_input])[0]

    # Search FAISS index to retrieve relevant file content
    distances, indices = search_index(faiss_index, input_embedding)

    # Retrieve relevant context from the file
    relevant_context = [vault_content[i] for i in indices[0]] if indices.size > 0 else []
    st.write("Relevant Context:", relevant_context)
    print("Relevant Context:", relevant_context)  # Debug line

    context_str = "\n".join(relevant_context) if relevant_context else "No relevant context found."

    # Prepare the user input with the relevant context (only for generating response)
    user_input_with_context = f"{user_input}\n\nContext:\n{context_str}" if relevant_context else user_input

    # Add only the user's input (without context) to chat history
    conversation_history.append({"role": "user", "content": user_input})

    # Prepare conversation history for the LLaMA model (without changing previous messages)
    messages = [{"role": "system", "content": "You are a helpful assistant"}] + conversation_history

    # Call LLaMA model with the current message history
    response = ollama.chat(model=ollama_model, messages=messages)

    # Add the model's response to the chat history
    conversation_history.append({"role": "assistant", "content": response['message']['content']})

    return response['message']['content']
