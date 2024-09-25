from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

def generate_embeddings(content_list):
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Using SentenceTransformer for embeddings
    embeddings = model.encode(content_list)
    return np.array(embeddings)

def index_embeddings(embeddings):
    dimension = embeddings.shape[1]  # Embedding dimension
    index = faiss.IndexFlatL2(dimension)  # L2 distance for search
    index.add(embeddings)  # Add the embeddings to the FAISS index
    return index

def search_index(index, query_embedding, top_k=3):
    query_embedding = np.array(query_embedding).reshape(1, -1)  # Reshape query for FAISS
    distances, indices = index.search(query_embedding, top_k)  # Search the index
    return distances, indices
