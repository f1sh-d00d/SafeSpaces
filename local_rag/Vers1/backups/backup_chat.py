'''
This file will handle the chatbot logic, 
including retrieving relevant context 
from the files and querying LLaMA 3.1 via the Ollama API.

This function:

Retrieves the context from uploaded files.
Combines user input with relevant content to pass to LLaMA 3.1 via Ollama.
Returns and displays the chatbot’s response.
'''
import ollama
from embeddings import search_index

def ollama_chat(user_input, faiss_index, vault_embeddings, vault_content, ollama_model, conversation_history):
    # Add user input to chat history
    conversation_history.append({"role": "user", "content": user_input})
    
    # Get embedding of user query
    input_embedding = ollama.embeddings(model=ollama_model, prompt=user_input)["embedding"]
    
    # Search FAISS index to retrieve relevant file content
    distances, indices = search_index(faiss_index, input_embedding)
    
    # Retrieve relevant context from the file
    relevant_context = [vault_content[i] for i in indices[0]]
    context_str = "\n".join(relevant_context) if relevant_context else "No relevant context found."
    
    # Append the context to user input
    user_input_with_context = f"{user_input}\n\nContext:\n{context_str}"
    conversation_history[-1]["content"] = user_input_with_context
    
    # Prepare conversation history for the LLaMA model
    messages = [{"role": "system", "content": "You are a helpful assistant."}] + conversation_history
    
    # Call Ollama's LLaMA model
    response = ollama.chat(model=ollama_model, messages=messages)
    
    # Add the assistant's response to the history
    conversation_history.append({"role": "assistant", "content": response['message']['content']})
    
    return response['message']['content']
