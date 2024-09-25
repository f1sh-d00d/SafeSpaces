from sentence_transformers import SentenceTransformer
from embeddings import search_index
import ollama

# Initialize the SentenceTransformer model once (ensure it matches the one in embeddings.py)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def ollama_chat(user_input, faiss_index, vault_embeddings, vault_content, ollama_model, conversation_history):
    # Add user input to chat history
    conversation_history.append({"role": "user", "content": user_input})

    # Generate embedding for the user query using the same model as file embeddings
    input_embedding = embedding_model.encode([user_input])

    # Search FAISS index to retrieve relevant file content
    distances, indices = search_index(faiss_index, input_embedding)

    # Retrieve relevant context from the file
    #print(f"Vault content: {vault_content}")
    relevant_context = [str(vault_content[i]) if isinstance(vault_content[i], dict) else vault_content[i] for i in indices[0]] #fixes error where we were trying to process dicts as strings. if a dict is passed here, we flatten it into a string
    context_str = "\n".join(relevant_context) if relevant_context else "No relevant context found."

    # Append the context to user input
    user_input_with_context = f"{user_input}\n\nContext:\n{context_str}"
    conversation_history[-1]["content"] = user_input_with_context

    # Prepare conversation history for the LLaMA model
    messages = [{"role": "system", "content": "You are a helpful assistant."}] + conversation_history

    # Call Ollama's LLaMA model for the chat
    response = ollama.chat(model=ollama_model, messages=messages)

    # Add the assistant's response to the history
    conversation_history.append({"role": "assistant", "content": response['message']['content']})

    return response['message']['content']
